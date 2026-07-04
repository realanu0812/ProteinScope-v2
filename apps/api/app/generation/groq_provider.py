import os

from dotenv import load_dotenv
from groq import Groq

from app.generation.provider import GenerationProvider


class GroqGenerationProvider(GenerationProvider):
    def __init__(self):
        load_dotenv()

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is missing. Add it to apps/api/.env")

        self.client = Groq(api_key=api_key)
        self._model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

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
