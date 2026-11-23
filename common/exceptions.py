class ErroDeDominio(Exception):
    """Base das violações de regra de negócio.

    A view captura este tipo e o traduz em mensagem para o usuário.
    """


class PermissaoNegadaError(ErroDeDominio):
    """O perfil do usuário não permite a operação."""


class DespesaNaoEncontradaError(ErroDeDominio):
    pass


class CoordenacaoNaoEncontradaError(ErroDeDominio):
    pass


class ComprovanteObrigatorioError(ErroDeDominio):
    """RN01: nenhuma despesa entra na fila sem comprovante."""


class JustificativaEstouroObrigatoriaError(ErroDeDominio):
    """RN02: aprovar despesa que ultrapassa o saldo exige justificativa."""


class SegregacaoDeFuncoesError(ErroDeDominio):
    """RN03: quem lançou a despesa não decide sobre ela."""


class ParecerObrigatorioError(ErroDeDominio):
    """RN04: rejeitar exige parecer."""


class DespesaImutavelError(ErroDeDominio):
    """RN05: depois de aprovada, a despesa não pode ser alterada."""


class TransicaoInvalidaError(ErroDeDominio):
    """A despesa não está no status exigido pela operação."""
