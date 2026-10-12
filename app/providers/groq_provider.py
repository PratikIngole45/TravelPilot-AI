import json
from typing import Type, TypeVar
from pydantic import BaseModel
from groq import Groq
from app.providers.llm_base import BaseLLMProvider
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import ProviderUnavailableError

T = TypeVar("T", bound=BaseModel)


class GroqProvider(BaseLLMProvider):
    """
    Groq LLM provider implementation for low-latency inference.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        if not self.api_key:
            raise ProviderUnavailableError("Groq API key not configured in environment (GROQ_API_KEY)")
        self.client = Groq(api_key=self.api_key, timeout=settings.REQUEST_TIMEOUT_SECONDS)

    def generate_structured_output(
        self,
        prompt: str,
        system_instruction: str,
        output_schema: Type[T]
    ) -> T:
        try:
            full_system = (
                f"{system_instruction}\n"
                f"You MUST reply with a single valid JSON object strictly complying with this schema:\n"
                f"{json.dumps(output_schema.model_json_schema())}"
            )
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": full_system},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            raw_json = completion.choices[0].message.content
            return output_schema.model_validate_json(raw_json)
        except Exception as e:
            logger.error(f"Groq API error during structured output: {str(e)}")
            raise ProviderUnavailableError(f"Groq service error: {str(e)}")

    def generate_answer(
        self,
        prompt: str,
        system_instruction: str,
        temperature: float = 0.2
    ) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            return completion.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Groq API error during answer generation: {str(e)}")
            raise ProviderUnavailableError(f"Groq service error: {str(e)}")
