"""Cog: Sistema do bebê virtual (wrapper do BebeSistema)."""
import logging

from nextcord.ext import commands

from bebe import BebeSistema, registrar_views_bebe

log = logging.getLogger(__name__)


class BebeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bebe_sistema = BebeSistema(bot)

    def _build_fresh_sistema(self) -> BebeSistema:
        # Evita manter instância antiga após reload parcial de extensão.
        self.bebe_sistema = BebeSistema(self.bot)
        return self.bebe_sistema

    @commands.Cog.listener()
    async def on_ready(self):
        sistema = self._build_fresh_sistema()

        try:
            registrar_views_bebe(self.bot, sistema)
            log.info("Views persistentes do bebê carregadas.")
        except Exception:
            log.exception("Erro ao carregar views do bebê")

        try:
            if not sistema.loop_bebe.is_running():
                sistema.loop_bebe.start()
                log.info("Loop do bebê iniciado.")
            else:
                log.info("Loop do bebê já estava rodando.")
        except Exception:
            log.exception("Erro ao iniciar loop do bebê")

            # Segunda tentativa com nova instância para evitar estado stale após reload.
            try:
                sistema = self._build_fresh_sistema()
                if not sistema.loop_bebe.is_running():
                    sistema.loop_bebe.start()
                    log.info("Loop do bebê iniciado na segunda tentativa.")
            except Exception:
                log.exception("Falha na segunda tentativa do loop do bebê")

        try:
            if not sistema.data.get("setup"):
                await sistema.atualizar_setup()
                log.info("Setup do bebê enviado/atualizado.")
            else:
                await sistema.atualizar_painel_principal()
                log.info("Painel principal do bebê enviado/atualizado.")
        except Exception:
            log.exception("Erro ao atualizar sistema do bebê")


def setup(bot: commands.Bot):
    bot.add_cog(BebeCog(bot))
