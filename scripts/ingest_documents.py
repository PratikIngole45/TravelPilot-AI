import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.rag.ingestion import DocumentIngestionPipeline
from app.core.logging import logger


def main():
    logger.info("Starting TravelPilot AI document ingestion...")
    pipeline = DocumentIngestionPipeline()
    total_chunks = pipeline.run_ingestion()
    print(f"Successfully ingested and indexed {total_chunks} chunks.")


if __name__ == "__main__":
    main()
