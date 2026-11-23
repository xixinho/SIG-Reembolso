from abc import ABC, abstractmethod

from common.enums import Perfil


class IAcessoService(ABC):
    @abstractmethod
    def perfil_de(self, usuario) -> Perfil:
        """Perfil do usuário; levanta PermissaoNegadaError se ele não tiver um."""

    @abstractmethod
    def coordenacao_id_de(self, usuario) -> int | None:
        """Coordenação a que o usuário pertence (None para o Administrador)."""

    @abstractmethod
    def pode_lancar(self, usuario) -> bool:
        """Coordenador e Tesouraria lançam despesas."""

    @abstractmethod
    def pode_triar(self, usuario) -> bool:
        """Só a Tesouraria aprova, rejeita e liquida."""

    @abstractmethod
    def pode_consultar_tudo(self, usuario) -> bool:
        """Tesouraria e Administrador veem as despesas de todas as coordenações."""
