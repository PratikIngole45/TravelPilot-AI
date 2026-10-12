from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def get_health():
    """
    Returns application health status and integration states without exposing secrets.
    """
    return {
        "status": "healthy",
        "app_env": settings.APP_ENV,
        "llm_provider": settings.LLM_PROVIDER,
        "has_groq_key": bool(settings.GROQ_API_KEY),
        "enable_neo4j": settings.ENABLE_NEO4J,
        "embedding_model": settings.EMBEDDING_MODEL
    }
