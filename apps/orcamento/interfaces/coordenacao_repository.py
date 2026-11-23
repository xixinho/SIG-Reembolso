from abc import ABC, abstractmethod

from apps.orcamento.models import Coordenacao


class ICoordenacaoRepository(ABC):
    @abstractmethod
    def obter(self, coordenacao_id: int) -> Coordenacao:
        """Levanta CoordenacaoNaoEncontradaError se não existir."""

    @abstractmethod
    def listar(self) -> list[Coordenacao]:
        pass
