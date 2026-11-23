from apps.accounts.interfaces.acesso_service import IAcessoService
from apps.accounts.models import PerfilUsuario
from common.enums import Perfil
from common.exceptions import PermissaoNegadaError


class AcessoService(IAcessoService):
    def perfil_de(self, usuario) -> Perfil:
        return Perfil(self._perfil_usuario(usuario).perfil)

    def coordenacao_id_de(self, usuario) -> int | None:
        return self._perfil_usuario(usuario).coordenacao_id

    def pode_lancar(self, usuario) -> bool:
        return self.perfil_de(usuario) in (Perfil.COORDENADOR, Perfil.TESOURARIA)

    def pode_triar(self, usuario) -> bool:
        return self.perfil_de(usuario) == Perfil.TESOURARIA

    def pode_consultar_tudo(self, usuario) -> bool:
        return self.perfil_de(usuario) in (Perfil.TESOURARIA, Perfil.ADMINISTRADOR)

    @staticmethod
    def _perfil_usuario(usuario) -> PerfilUsuario:
        try:
            return PerfilUsuario.objects.get(usuario_id=usuario.id)
        except PerfilUsuario.DoesNotExist as erro:
            raise PermissaoNegadaError("Usuário sem perfil de acesso.") from erro
