from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(ABC):
    """
    Abstract interface for LLM providers ensuring swappable model backends.
    """

    @abstractmethod
    def generate_structured_output(
        self,
        prompt: str,
        system_instruction: str,
        output_schema: Type[T]
    ) -> T:
        """
        Generates schema-validated structured output matching output_schema.
        """
        pass

    @abstractmethod
    def generate_answer(
        self,
        prompt: str,
        system_instruction: str,
        temperature: float = 0.2
    ) -> str:
        """
        Generates grounded conversational text response.
        """
        pass
