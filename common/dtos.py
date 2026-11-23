from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class DadosDespesa:
    """Dados informados pelo usuário ao lançar ou editar uma despesa.

    Na edição, ``comprovante=None`` mantém o comprovante atual.
    """

    tipo: str
    descricao: str
    valor: Decimal
    data_compra: date
    beneficiario: str
    chave_pix: str
    comprovante: Any = None
