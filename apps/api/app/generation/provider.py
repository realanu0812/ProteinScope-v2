from abc import ABC, abstractmethod


class GenerationProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

    @abstractmethod
    def model_name(self) -> str:
        pass
