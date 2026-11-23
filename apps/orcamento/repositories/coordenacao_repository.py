from apps.orcamento.interfaces.coordenacao_repository import ICoordenacaoRepository
from apps.orcamento.models import Coordenacao
from common.exceptions import CoordenacaoNaoEncontradaError


class CoordenacaoRepository(ICoordenacaoRepository):
    def obter(self, coordenacao_id: int) -> Coordenacao:
        try:
            return Coordenacao.objects.get(pk=coordenacao_id)
        except Coordenacao.DoesNotExist as erro:
            raise CoordenacaoNaoEncontradaError(
                f"Coordenação {coordenacao_id} não encontrada."
            ) from erro

    def listar(self) -> list[Coordenacao]:
        return list(Coordenacao.objects.all())
