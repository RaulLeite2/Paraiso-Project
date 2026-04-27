"""Cog: Sistema do bebê virtual (wrapper do BebeSistema)."""
import logging

from nextcord.ext import commands

from bebe import BebeSistema, registrar_views_bebe

log = logging.getLogger(__name__)


class BebeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bebe_sistema = BebeSistema(bot)

    def _get_sistema(self) -> BebeSistema:
        # Garante instância válida mesmo após reload parcial da cog.
        sistema = getattr(self, "bebe_sistema", None)
        if sistema is None:
            sistema = BebeSistema(self.bot)
            self.bebe_sistema = sistema
        return sistema

    @commands.Cog.listener()
    async def on_ready(self):
        sistema = self._get_sistema()

        try:
            registrar_views_bebe(self.bot, sistema)
            log.info("Views persistentes do bebê carregadas.")
        except Exception as e:
            log.error(f"Erro ao carregar views do bebê: {e}")

        try:
            if not sistema.loop_bebe.is_running():
                sistema.iniciar_loops()
                log.info("Loop do bebê iniciado.")
            else:
                log.info("Loop do bebê já estava rodando.")
        except Exception as e:
            log.error(f"Erro ao iniciar loop do bebê: {e}")

        try:
            if not sistema.data.get("setup"):
                await sistema.atualizar_setup()
                log.info("Setup do bebê enviado/atualizado.")
            else:
                await sistema.atualizar_painel_principal()
                log.info("Painel principal do bebê enviado/atualizado.")
        except Exception as e:
            log.error(f"Erro ao atualizar sistema do bebê: {e}")


def setup(bot: commands.Bot):
    bot.add_cog(BebeCog(bot))
