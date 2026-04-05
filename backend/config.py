import os
from dataclasses import dataclass


def get_secret(secret_id: str, project_id: str) -> str:
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("utf-8")


def resolve(env_var: str, secret_id: str, project_id: str) -> str:
    value = os.environ.get(env_var)
    if value:
        return value
    return get_secret(secret_id, project_id)


@dataclass
class Config:
    google_api_key: str
    langchain_api_key: str
    deepeval_api_key: str
    model_name: str
    temperature: float
    langsmith_tracing: bool
    langsmith_project: str
    project_id: str

    @classmethod
    def from_env(cls) -> "Config":
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise EnvironmentError(
                "GOOGLE_CLOUD_PROJECT is not set. "
                "Run: export GOOGLE_CLOUD_PROJECT='your-project-id'"
            )

        deepeval_api_key = resolve("DEEPEVAL_API_KEY", "DEEPEVAL_API_KEY", project_id)
        google_api_key = resolve("GOOGLE_API_KEY", "GOOGLE_API_KEY", project_id)
        if not google_api_key:
            raise EnvironmentError("GOOGLE_API_KEY could not be resolved.")

        langchain_api_key = resolve("LANGCHAIN_API_KEY", "LANGCHAIN_API_KEY", project_id)

        return cls(
            google_api_key=google_api_key,
            langchain_api_key=langchain_api_key,
            model_name=os.environ.get("MODEL_NAME", "gemini-2.5-flash-lite"),
            temperature=float(os.environ.get("TEMPERATURE", "0")),
            langsmith_tracing=os.environ.get("LANGCHAIN_TRACING_V2", "false").lower() == "true",
            langsmith_project=os.environ.get("LANGCHAIN_PROJECT", "paper-to-articles"),
            project_id=project_id,
            deepeval_api_key=deepeval_api_key,
        )


config = Config.from_env()
