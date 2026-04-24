import nextcord

def create_welcome_embed(bot, user):
    embed = nextcord.Embed(
        description=(
            f"**Habilitado por** {user.mention} • agora\n\n"
            "Alertas de boas-vindas estão ativos para este servidor. "
            "O sistema irá recepcionar novos membros automaticamente "
            "e garantir uma experiência agradável desde a chegada."
        ),
        color=0x313338  # cor EXATA do Discord
    )

    # título verde fake (usando emoji)
    embed.title = "🟢 Boas-vindas ativadas"

    # autor estilo sistema
    embed.set_author(
        name="Sistema",
        icon_url=bot.user.display_avatar.url
    )

    return embed