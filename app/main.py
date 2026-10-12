from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.api.routes_health import router as health_router
from app.api.routes_destinations import router as destinations_router
from app.api.routes_trips import router as trips_router
from app.api.routes_qa import router as qa_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm embedding model and vector store so first request responds instantly
    logger.info("Pre-warming RAG vector store and SentenceTransformer embedding model...")
    try:
        from app.rag.retriever import TravelRetriever
        retriever = TravelRetriever()
        logger.info(f"RAG vector store ready with {len(retriever.vector_store.chunks)} chunks.")
    except Exception as e:
        logger.warning(f"RAG warmup exception (will load on demand): {e}")
    yield


app = FastAPI(
    title="TravelPilot AI",
    description="Intelligent Travel Planning Agent with RAG, Knowledge Graph, and Deterministic Constraints",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health_router)
app.include_router(destinations_router)
app.include_router(trips_router)
app.include_router(qa_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming {request.method} request to {request.url.path}")
    response = await call_next(request)
    logger.info(f"Completed {request.method} {request.url.path} with status {response.status_code}")
    return response


@app.get("/")
def root():
    return {
        "message": "Welcome to TravelPilot AI API",
        "docs": "/docs",
        "health": "/health",
        "version": "0.1.0"
    }
