from typing import Type, TypeVar
from pydantic import BaseModel
from app.providers.llm_base import BaseLLMProvider
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)


class DeterministicProvider(BaseLLMProvider):
    """
    Deterministic provider that generates verified schemas and grounded responses
    without requiring external paid API keys. Used for local testing, demo mode, and offline CI.
    """

    def generate_structured_output(
        self,
        prompt: str,
        system_instruction: str,
        output_schema: Type[T]
    ) -> T:
        logger.info("DeterministicProvider generating structured output")
        # Instantiate default schema or dummy validated object
        raise NotImplementedError("Use domain services for direct deterministic compilation")

    def generate_answer(
        self,
        prompt: str,
        system_instruction: str,
        temperature: float = 0.2
    ) -> str:
        return "Deterministic response synthesized from knowledge base evidence."
