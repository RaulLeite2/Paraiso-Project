import os
import json
from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands


CANAL_CASAMENTO_ID = 1494420437453635766

# TROCA AQUI
SEU_ID = 1431111401522462741
ID_DA_NOIVA = 715329753032163379

ARQUIVO_CASAMENTO = "casamento_compatibilidade.json"
ARQUIVO_ECONOMIA = "database.json"


# =========================
# UTILITÁRIOS JSON
# =========================

def carregar_json(caminho: str, default):
    if not os.path.exists(caminho):
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=4, ensure_ascii=False)
        return default

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def salvar_json(caminho: str, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def now_iso():
    return datetime.utcnow().isoformat()


# =========================
# DADOS BASE
# =========================

def estrutura_casamento():
    return {
        "canal_id": CANAL_CASAMENTO_ID,
        "casal_ids": [SEU_ID, ID_DA_NOIVA],
        "usuarios": {
            str(SEU_ID): {
                "respostas": {},
                "pronto_resultado": False,
                "ultimo_envio": None
            },
            str(ID_DA_NOIVA): {
                "respostas": {},
                "pronto_resultado": False,
                "ultimo_envio": None
            }
        },
        "ultima_rodada_id": 0,
        "ultimo_resultado": None,
        "recompensas_entregues": []
    }


def carregar_dados_casamento():
    dados = carregar_json(ARQUIVO_CASAMENTO, estrutura_casamento())

    # garante estrutura
    for uid in [str(SEU_ID), str(ID_DA_NOIVA)]:
        if "usuarios" not in dados:
            dados["usuarios"] = {}
        if uid not in dados["usuarios"]:
            dados["usuarios"][uid] = {
                "respostas": {},
                "pronto_resultado": False,
                "ultimo_envio": None
            }

    if "recompensas_entregues" not in dados:
        dados["recompensas_entregues"] = []

    if "ultima_rodada_id" not in dados:
        dados["ultima_rodada_id"] = 0

    return dados


def salvar_dados_casamento(dados):
    salvar_json(ARQUIVO_CASAMENTO, dados)


def carregar_economia():
    return carregar_json(ARQUIVO_ECONOMIA, {})


def salvar_economia(dados):
    salvar_json(ARQUIVO_ECONOMIA, dados)


def garantir_usuario_economia(user_id: int):
    dados = carregar_economia()
    uid = str(user_id)

    if uid not in dados:
        dados[uid] = {
            "moedas": 0,
            "mimos": 0
        }
    else:
        if "moedas" not in dados[uid]:
            dados[uid]["moedas"] = 0
        if "mimos" not in dados[uid]:
            dados[uid]["mimos"] = 0

    salvar_economia(dados)
    return dados


def adicionar_recompensa(user_id: int, moedas: int = 0, mimos: int = 0):
    dados = garantir_usuario_economia(user_id)
    uid = str(user_id)

    dados[uid]["moedas"] += moedas
    dados[uid]["mimos"] += mimos

    salvar_economia(dados)


# =========================
# OPÇÕES DO SISTEMA
# =========================

LUGARES = [
    ("praia", "Praia"),
    ("igreja", "Igreja"),
    ("campo", "Campo / Sítio"),
    ("salao", "Salão elegante"),
    ("jardim", "Jardim"),
    ("simples", "Algo simples / íntimo"),
]

BOLOS = [
    ("chocolate", "Chocolate"),
    ("morango", "Morango"),
    ("red_velvet", "Red Velvet"),
    ("ninho", "Ninho"),
    ("baunilha", "Baunilha"),
    ("prestigio", "Prestígio"),
    ("doce_de_leite", "Doce de leite"),
]

MUSICAS = [
    ("romantico", "Romântico"),
    ("sertanejo", "Sertanejo"),
    ("pop", "Pop"),
    ("pagode", "Pagode"),
    ("mpb", "MPB"),
    ("gospel", "Gospel"),
    ("funk", "Funk"),
    ("eletronica", "Eletrônica"),
]

PERIODOS = [
    ("manha", "Manhã"),
    ("tarde", "Tarde"),
    ("por_do_sol", "Pôr do sol"),
    ("noite", "Noite"),
]

QTD_CONVIDADOS = [
    ("mini", "Só nós dois / mini cerimônia"),
    ("intimo", "Bem íntimo"),
    ("pequeno", "Pequeno"),
    ("medio", "Médio"),
    ("grande", "Grande"),
    ("muita_gente", "Muita gente"),
]

TIPO_CONVIDADOS = [
    ("familia_proxima", "Só família próxima"),
    ("familia_amigos_proximos", "Família + amigos próximos"),
    ("misto", "Família + amigos + alguns conhecidos"),
    ("todos_importantes", "Todo mundo importante"),
    ("festa_grande", "Festa grande com conhecidos também"),
]

DECORACOES = [
    ("luxuosa", "Luxuosa"),
    ("minimalista", "Minimalista"),
    ("romantica", "Romântica"),
    ("floral", "Floral"),
    ("elegante_escura", "Elegante escura"),
    ("fofa", "Fofa / delicada"),
    ("rustica", "Rústica"),
]


def label_de(opcoes, valor):
    for k, v in opcoes:
        if k == valor:
            return v
    return valor


# =========================
# REGRAS DE COMPATIBILIDADE
# =========================

ORDENACAO_PERIODO = {
    "manha": 0,
    "tarde": 1,
    "por_do_sol": 2,
    "noite": 3,
}

ORDENACAO_CONVIDADOS = {
    "mini": 0,
    "intimo": 1,
    "pequeno": 2,
    "medio": 3,
    "grande": 4,
    "muita_gente": 5,
}

ORDENACAO_TIPO = {
    "familia_proxima": 0,
    "familia_amigos_proximos": 1,
    "misto": 2,
    "todos_importantes": 3,
    "festa_grande": 4,
}


def pontuar_igual(a, b):
    return 10 if a == b else 0


def pontuar_proximidade(mapa, a, b):
    if a == b:
        return 10

    da = mapa.get(a, 999)
    db = mapa.get(b, 999)
    diff = abs(da - db)

    if diff == 1:
        return 5
    return 0


def pontuar_multiselect(lista_a, lista_b):
    set_a = set(lista_a)
    set_b = set(lista_b)
    comuns = len(set_a & set_b)

    if comuns >= 2:
        return 10
    if comuns == 1:
        return 5
    return 0


def validar_respostas_completas(respostas: dict):
    campos = [
        "lugar",
        "bolo",
        "musica",
        "periodo",
        "qtd_convidados",
        "tipo_convidados",
        "decoracao"
    ]

    for campo in campos:
        if campo not in respostas:
            return False

    if not isinstance(respostas.get("bolo"), list) or len(respostas["bolo"]) != 2:
        return False

    if not isinstance(respostas.get("musica"), list) or len(respostas["musica"]) != 2:
        return False

    return True


def nivel_compatibilidade(porcentagem: int):
    if porcentagem <= 20:
        return "Casamento caótico 😭"
    elif porcentagem <= 40:
        return "Vai precisar de negociação 😂"
    elif porcentagem <= 60:
        return "Tem química, mas precisam alinhar 💫"
    elif porcentagem <= 80:
        return "Casal bem conectado 💕"
    return "Almas gêmeas do altar 💍"


def calcular_compatibilidade(r1: dict, r2: dict):
    total = 0
    maximo = 70

    compatibilidades = []
    divergencias = []

    # Lugar
    p = pontuar_igual(r1["lugar"], r2["lugar"])
    total += p
    if p == 10:
        compatibilidades.append(f"📍 Lugar: {label_de(LUGARES, r1['lugar'])}")
    else:
        divergencias.append(
            f"📍 Lugar: {label_de(LUGARES, r1['lugar'])} x {label_de(LUGARES, r2['lugar'])}"
        )

    # Bolo
    p = pontuar_multiselect(r1["bolo"], r2["bolo"])
    total += p
    comuns_bolo = list(set(r1["bolo"]) & set(r2["bolo"]))
    if p == 10:
        compatibilidades.append(
            f"🎂 Bolo: 2 sabores em comum ({', '.join(label_de(BOLOS, x) for x in comuns_bolo)})"
        )
    elif p == 5:
        compatibilidades.append(
            f"🎂 Bolo: 1 sabor em comum ({label_de(BOLOS, comuns_bolo[0])})"
        )
    else:
        divergencias.append(
            f"🎂 Bolo: {', '.join(label_de(BOLOS, x) for x in r1['bolo'])} x {', '.join(label_de(BOLOS, x) for x in r2['bolo'])}"
        )

    # Música
    p = pontuar_multiselect(r1["musica"], r2["musica"])
    total += p
    comuns_musica = list(set(r1["musica"]) & set(r2["musica"]))
    if p == 10:
        compatibilidades.append(
            f"🎵 Música: 2 gêneros em comum ({', '.join(label_de(MUSICAS, x) for x in comuns_musica)})"
        )
    elif p == 5:
        compatibilidades.append(
            f"🎵 Música: 1 gênero em comum ({label_de(MUSICAS, comuns_musica[0])})"
        )
    else:
        divergencias.append(
            f"🎵 Música: {', '.join(label_de(MUSICAS, x) for x in r1['musica'])} x {', '.join(label_de(MUSICAS, x) for x in r2['musica'])}"
        )

    # Período
    p = pontuar_proximidade(ORDENACAO_PERIODO, r1["periodo"], r2["periodo"])
    total += p
    if p == 10:
        compatibilidades.append(f"🌅 Período: {label_de(PERIODOS, r1['periodo'])}")
    elif p == 5:
        compatibilidades.append(
            f"🌅 Período parecido: {label_de(PERIODOS, r1['periodo'])} x {label_de(PERIODOS, r2['periodo'])}"
        )
    else:
        divergencias.append(
            f"🌅 Período: {label_de(PERIODOS, r1['periodo'])} x {label_de(PERIODOS, r2['periodo'])}"
        )

    # Quantidade convidados
    p = pontuar_proximidade(ORDENACAO_CONVIDADOS, r1["qtd_convidados"], r2["qtd_convidados"])
    total += p
    if p == 10:
        compatibilidades.append(f"👥 Quantidade de convidados: {label_de(QTD_CONVIDADOS, r1['qtd_convidados'])}")
    elif p == 5:
        compatibilidades.append(
            f"👥 Quantidade parecida: {label_de(QTD_CONVIDADOS, r1['qtd_convidados'])} x {label_de(QTD_CONVIDADOS, r2['qtd_convidados'])}"
        )
    else:
        divergencias.append(
            f"👥 Quantidade: {label_de(QTD_CONVIDADOS, r1['qtd_convidados'])} x {label_de(QTD_CONVIDADOS, r2['qtd_convidados'])}"
        )

    # Tipo convidados
    p = pontuar_proximidade(ORDENACAO_TIPO, r1["tipo_convidados"], r2["tipo_convidados"])
    total += p
    if p == 10:
        compatibilidades.append(f"💌 Tipo de convidados: {label_de(TIPO_CONVIDADOS, r1['tipo_convidados'])}")
    elif p == 5:
        compatibilidades.append(
            f"💌 Tipo parecido: {label_de(TIPO_CONVIDADOS, r1['tipo_convidados'])} x {label_de(TIPO_CONVIDADOS, r2['tipo_convidados'])}"
        )
    else:
        divergencias.append(
            f"💌 Tipo de convidados: {label_de(TIPO_CONVIDADOS, r1['tipo_convidados'])} x {label_de(TIPO_CONVIDADOS, r2['tipo_convidados'])}"
        )

    # Decoração
    p = pontuar_igual(r1["decoracao"], r2["decoracao"])
    total += p
    if p == 10:
        compatibilidades.append(f"🎀 Decoração: {label_de(DECORACOES, r1['decoracao'])}")
    else:
        divergencias.append(
            f"🎀 Decoração: {label_de(DECORACOES, r1['decoracao'])} x {label_de(DECORACOES, r2['decoracao'])}"
        )

    porcentagem = round((total / maximo) * 100)
    return {
        "pontos": total,
        "maximo": maximo,
        "porcentagem": porcentagem,
        "nivel": nivel_compatibilidade(porcentagem),
        "compatibilidades": compatibilidades,
        "divergencias": divergencias
    }


def calcular_recompensa(porcentagem: int):
    if porcentagem == 100:
        return {"moedas": 20, "mimos": 1}
    elif porcentagem >= 90:
        return {"moedas": 10, "mimos": 1}
    elif porcentagem >= 70:
        return {"moedas": 10, "mimos": 0}
    else:
        return {"moedas": 5, "mimos": 0}


# =========================
# EMBEDS
# =========================

def criar_embed_painel():
    embed = discord.Embed(
        title="💍 Compatibilidade do Casamento",
        description=(
            "Clique no botão abaixo para montar as suas escolhas do grande dia.\n\n"
            "Quando **os dois** enviarem e estiverem prontos, o bot revela a compatibilidade juntos. 💖"
        ),
        color=discord.Color.pink()
    )
    embed.set_footer(text="Casamento interativo do servidor")
    return embed


def criar_embed_menu(usuario: discord.User):
    embed = discord.Embed(
        title="💌 Seu painel de compatibilidade",
        description=(
            f"Oi, {usuario.mention}.\n\n"
            "Use os botões abaixo para preencher, editar ou confirmar suas escolhas."
        ),
        color=discord.Color.from_rgb(255, 105, 180)
    )
    return embed


def criar_embed_resultado(bot: commands.Bot, resultado: dict):
    user1 = bot.get_user(SEU_ID)
    user2 = bot.get_user(ID_DA_NOIVA)

    nome1 = user1.mention if user1 else f"<@{SEU_ID}>"
    nome2 = user2.mention if user2 else f"<@{ID_DA_NOIVA}>"

    barra = "█" * max(1, resultado["porcentagem"] // 10) + "░" * (10 - max(1, resultado["porcentagem"] // 10))

    embed = discord.Embed(
        title="💍 Resultado da Compatibilidade",
        description=(
            f"{nome1} + {nome2}\n\n"
            f"**Compatibilidade final:** `{resultado['porcentagem']}%`\n"
            f"`{barra}`\n"
            f"**Nível:** {resultado['nivel']}"
        ),
        color=discord.Color.gold()
    )

    embed.add_field(
        name="✅ Compatibilidades",
        value="\n".join(resultado["compatibilidades"][:10]) if resultado["compatibilidades"] else "Nenhuma compatibilidade encontrada.",
        inline=False
    )

    embed.add_field(
        name="❌ Diferenças",
        value="\n".join(resultado["divergencias"][:10]) if resultado["divergencias"] else "Nenhuma diferença encontrada.",
        inline=False
    )

    recompensa = calcular_recompensa(resultado["porcentagem"])
    embed.add_field(
        name="🎁 Recompensas",
        value=f"+{recompensa['moedas']} moedas para cada"
              + (f"\n+{recompensa['mimos']} mimo(s) para cada" if recompensa["mimos"] > 0 else ""),
        inline=False
    )

    embed.set_footer(text="O amor venceu mais uma escolha do casamento 💖")
    return embed


# =========================
# MODAIS
# =========================

class LugarSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=label, value=value)
            for value, label in LUGARES
        ]
        super().__init__(
            placeholder="Escolha o lugar do casamento...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        salvar_resposta(interaction.user.id, "lugar", self.values[0], resetar_pronto=True)
        await interaction.response.send_message("📍 Lugar salvo com sucesso.", ephemeral=True)


class BoloSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=label, value=value)
            for value, label in BOLOS
        ]
        super().__init__(
            placeholder="Escolha 2 sabores de bolo...",
            min_values=2,
            max_values=2,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        salvar_resposta(interaction.user.id, "bolo", self.values, resetar_pronto=True)
        await interaction.response.send_message("🎂 Sabores do bolo salvos com sucesso.", ephemeral=True)


class MusicaSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=label, value=value)
            for value, label in MUSICAS
        ]
        super().__init__(
            placeholder="Escolha 2 gêneros musicais...",
            min_values=2,
            max_values=2,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        salvar_resposta(interaction.user.id, "musica", self.values, resetar_pronto=True)
        await interaction.response.send_message("🎵 Gêneros musicais salvos com sucesso.", ephemeral=True)


class PeriodoSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=label, value=value)
            for value, label in PERIODOS
        ]
        super().__init__(
            placeholder="Escolha o período do casamento...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        salvar_resposta(interaction.user.id, "periodo", self.values[0], resetar_pronto=True)
        await interaction.response.send_message("🌅 Período salvo com sucesso.", ephemeral=True)


class QtdConvidadosSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=label, value=value)
            for value, label in QTD_CONVIDADOS
        ]
        super().__init__(
            placeholder="Escolha a quantidade de convidados...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        salvar_resposta(interaction.user.id, "qtd_convidados", self.values[0], resetar_pronto=True)
        await interaction.response.send_message("👥 Quantidade de convidados salva com sucesso.", ephemeral=True)


class TipoConvidadosSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=label, value=value)
            for value, label in TIPO_CONVIDADOS
        ]
        super().__init__(
            placeholder="Escolha o tipo de convidados...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        salvar_resposta(interaction.user.id, "tipo_convidados", self.values[0], resetar_pronto=True)
        await interaction.response.send_message("💌 Tipo de convidados salvo com sucesso.", ephemeral=True)


class DecoracaoSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=label, value=value)
            for value, label in DECORACOES
        ]
        super().__init__(
            placeholder="Escolha o estilo da decoração...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        salvar_resposta(interaction.user.id, "decoracao", self.values[0], resetar_pronto=True)
        await interaction.response.send_message("🎀 Decoração salva com sucesso.", ephemeral=True)


# =========================
# VIEWS
# =========================

def usuario_autorizado(user_id: int):
    return user_id in [SEU_ID, ID_DA_NOIVA]


def salvar_resposta(user_id: int, campo: str, valor, resetar_pronto: bool = True):
    dados = carregar_dados_casamento()
    uid = str(user_id)

    if uid not in dados["usuarios"]:
        dados["usuarios"][uid] = {
            "respostas": {},
            "pronto_resultado": False,
            "ultimo_envio": None
        }

    dados["usuarios"][uid]["respostas"][campo] = valor

    if resetar_pronto:
        dados["usuarios"][uid]["pronto_resultado"] = False

    salvar_dados_casamento(dados)


class FormularioCompatibilidadeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

        self.add_item(LugarSelect())
        self.add_item(BoloSelect())
        self.add_item(MusicaSelect())
        self.add_item(PeriodoSelect())
        self.add_item(QtdConvidadosSelect())
        self.add_item(TipoConvidadosSelect())
        self.add_item(DecoracaoSelect())


class MenuCompatibilidadeView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=300)
        self.bot = bot

    @discord.ui.button(label="📋 Ir para as opções", style=discord.ButtonStyle.primary)
    async def ir_opcoes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not usuario_autorizado(interaction.user.id):
            await interaction.response.send_message("❌ Só o casal pode usar esse painel.", ephemeral=True)
            return

        await interaction.response.send_message(
            "Escolha suas opções abaixo. Sempre que editar algo, seu status de pronto será resetado.",
            view=FormularioCompatibilidadeView(),
            ephemeral=True
        )

    @discord.ui.button(label="✏️ Editar informações", style=discord.ButtonStyle.secondary)
    async def editar_infos(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not usuario_autorizado(interaction.user.id):
            await interaction.response.send_message("❌ Só o casal pode usar esse painel.", ephemeral=True)
            return

        dados = carregar_dados_casamento()
        uid = str(interaction.user.id)
        respostas = dados["usuarios"].get(uid, {}).get("respostas", {})

        if not respostas:
            await interaction.response.send_message(
                "⚠️ Você ainda não tem informações salvas. Preencha primeiro em `Ir para as opções`.",
                ephemeral=True
            )
            return

        dados["usuarios"][uid]["pronto_resultado"] = False
        salvar_dados_casamento(dados)

        await interaction.response.send_message(
            "✏️ Você entrou no modo de edição. Mude o que quiser abaixo e depois clique em `Enviar e ver resultado` novamente.",
            view=FormularioCompatibilidadeView(),
            ephemeral=True
        )

    @discord.ui.button(label="📨 Enviar e ver resultado", style=discord.ButtonStyle.success)
    async def enviar_ver_resultado(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not usuario_autorizado(interaction.user.id):
            await interaction.response.send_message("❌ Só o casal pode usar esse painel.", ephemeral=True)
            return

        dados = carregar_dados_casamento()
        uid = str(interaction.user.id)

        respostas = dados["usuarios"][uid]["respostas"]
        if not validar_respostas_completas(respostas):
            await interaction.response.send_message(
                "⚠️ Você ainda não respondeu tudo. Complete todas as opções antes de enviar.",
                ephemeral=True
            )
            return

        dados["usuarios"][uid]["pronto_resultado"] = True
        dados["usuarios"][uid]["ultimo_envio"] = now_iso()
        salvar_dados_casamento(dados)

        outro_id = SEU_ID if interaction.user.id == ID_DA_NOIVA else ID_DA_NOIVA
        outro_uid = str(outro_id)
        outro_pronto = dados["usuarios"][outro_uid]["pronto_resultado"]
        outro_completo = validar_respostas_completas(dados["usuarios"][outro_uid]["respostas"])

        if not outro_completo or not outro_pronto:
            await interaction.response.send_message(
                "💌 Suas informações foram enviadas. Agora falta a outra pessoa ficar pronta para vocês verem o resultado juntos.",
                ephemeral=True
            )
            return

        # ambos prontos -> gerar resultado
        r1 = dados["usuarios"][str(SEU_ID)]["respostas"]
        r2 = dados["usuarios"][str(ID_DA_NOIVA)]["respostas"]
        resultado = calcular_compatibilidade(r1, r2)

        dados["ultima_rodada_id"] += 1
        rodada_id = dados["ultima_rodada_id"]

        dados["ultimo_resultado"] = {
            "rodada_id": rodada_id,
            "gerado_em": now_iso(),
            "porcentagem": resultado["porcentagem"],
            "nivel": resultado["nivel"],
            "compatibilidades": resultado["compatibilidades"],
            "divergencias": resultado["divergencias"]
        }

        # reseta os dois prontos depois de mostrar
        dados["usuarios"][str(SEU_ID)]["pronto_resultado"] = False
        dados["usuarios"][str(ID_DA_NOIVA)]["pronto_resultado"] = False

        salvar_dados_casamento(dados)

        # entrega recompensa se ainda não entregou nessa rodada
        recompensa_key = f"rodada_{rodada_id}"
        dados = carregar_dados_casamento()

        if recompensa_key not in dados["recompensas_entregues"]:
            recompensa = calcular_recompensa(resultado["porcentagem"])
            adicionar_recompensa(SEU_ID, moedas=recompensa["moedas"], mimos=recompensa["mimos"])
            adicionar_recompensa(ID_DA_NOIVA, moedas=recompensa["moedas"], mimos=recompensa["mimos"])
            dados["recompensas_entregues"].append(recompensa_key)
            salvar_dados_casamento(dados)

        embed = criar_embed_resultado(self.bot, resultado)

        canal = self.bot.get_channel(CANAL_CASAMENTO_ID)
        if canal:
            await canal.send(embed=embed)

        await interaction.response.send_message(
            "💍 Os dois estão prontos. A compatibilidade foi revelada no canal de casamento!",
            ephemeral=True
        )


class PainelCompatibilidadeView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="💍 Começar compatibilidade", style=discord.ButtonStyle.success, custom_id="casamento_comecar")
    async def comecar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not usuario_autorizado(interaction.user.id):
            await interaction.response.send_message(
                "❌ Esse painel é exclusivo do casal.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            embed=criar_embed_menu(interaction.user),
            view=MenuCompatibilidadeView(self.bot),
            ephemeral=True
        )


# =========================
# COG
# =========================

class Casamento(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.add_view(PainelCompatibilidadeView(bot))

    @commands.command(name="painelcasamento")
    async def painel_casamento(self, ctx: commands.Context):
        if ctx.channel.id != CANAL_CASAMENTO_ID:
            await ctx.send("❌ Esse comando só pode ser usado no canal de casamento.")
            return

        embed = criar_embed_painel()
        view = PainelCompatibilidadeView(self.bot)
        await ctx.send(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Casamento(bot))