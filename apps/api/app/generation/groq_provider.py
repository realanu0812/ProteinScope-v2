from groq import Groq

from app.config import get_config, validate_generation_config
from app.generation.provider import GenerationProvider


class GroqGenerationProvider(GenerationProvider):
    def __init__(self):
        validate_generation_config()

        config = get_config()

        self.client = Groq(api_key=config.groq_api_key)
        self._model_name = config.groq_model

    def model_name(self) -> str:
        return self._model_name

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self._model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are ProteinScope, a scientific assistant that answers only from provided context.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
            max_tokens=700,
        )

        return response.choices[0].message.content or ""
