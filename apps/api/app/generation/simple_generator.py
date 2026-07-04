from app.generation.provider import GenerationProvider


class SimpleExtractiveGenerator(GenerationProvider):
    """
    Temporary mock generator.

    It does not call an LLM yet.
    It returns a grounded extractive answer from retrieved context.

    This lets us test:
    - retrieval
    - citation formatting
    - answer endpoint structure

    Later we replace this with Groq/OpenAI/Gemini.
    """

    def model_name(self) -> str:
        return "simple-extractive-generator"

    def generate(self, prompt: str) -> str:
        return (
            "Based on the retrieved document sections, the answer should be derived from the cited sources below. "
            "This endpoint is currently using a simple extractive generator; an LLM provider will be added next."
        )
