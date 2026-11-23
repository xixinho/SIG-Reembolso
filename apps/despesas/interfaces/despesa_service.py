from abc import ABC, abstractmethod

from apps.despesas.models import Despesa
from common.dtos import DadosDespesa


class IDespesaService(ABC):
    @abstractmethod
    def lancar(self, dados: DadosDespesa, solicitante) -> Despesa:
        """Lança na coordenação do solicitante (RN01)."""

    @abstractmethod
    def editar(self, despesa_id: int, usuario, dados: DadosDespesa) -> Despesa:
        """Só o solicitante, só enquanto PENDENTE (RN05)."""

    @abstractmethod
    def cancelar(self, despesa_id: int, usuario) -> Despesa:
        """Só o solicitante, só enquanto PENDENTE (RN05)."""

    @abstractmethod
    def aprovar(
        self,
        despesa_id: int,
        usuario,
        justificativa_estouro: str | None = None,
    ) -> Despesa:
        """Tesouraria; RN03 e RN02 (estouro exige justificativa)."""

    @abstractmethod
    def rejeitar(self, despesa_id: int, usuario, parecer: str) -> Despesa:
        """Tesouraria; RN03 e RN04 (parecer obrigatório)."""

    @abstractmethod
    def liquidar(self, despesa_id: int, usuario, comprovante_pagamento) -> Despesa:
        """Tesouraria; despesa APROVADA, com o comprovante do pagamento."""

    @abstractmethod
    def fila_triagem(self, usuario) -> list[Despesa]:
        """Despesas pendentes, para a Tesouraria."""

    @abstractmethod
    def extrato(self, usuario, coordenacao_id: int | None = None) -> list[Despesa]:
        """Coordenador e tesoureiro veem a própria coordenação; Tesouraria e
        Administrador podem ver qualquer uma ou todas."""
