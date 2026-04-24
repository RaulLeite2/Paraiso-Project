import json

ARQUIVO = "database.json"



def carregar():
    try:
        with open(ARQUIVO, "r") as f:
            return json.load(f)
    except:
        return {}

def salvar(dados):
    with open(ARQUIVO, "w") as f:
        json.dump(dados, f, indent=4)

def get_user(user_id):
    dados = carregar()
    if str(user_id) not in dados:
        dados[str(user_id)] = {"moedas": 0, "mimos": 0}
        salvar(dados)
    return dados

# ===== MOEDAS =====
def add_moedas(user_id, valor):
    dados = get_user(user_id)
    dados[str(user_id)]["moedas"] += valor
    salvar(dados)

def get_moedas(user_id):
    dados = get_user(user_id)
    return dados[str(user_id)]["moedas"]

# ===== MIMOS =====
def add_mimos(user_id, valor):
    dados = get_user(user_id)
    dados[str(user_id)]["mimos"] += valor
    salvar(dados)

def get_mimos(user_id):
    dados = get_user(user_id)
    return dados[str(user_id)]["mimos"]

def remove_mimos(user_id, valor):
    dados = get_user(user_id)
    dados[str(user_id)]["mimos"] = max(0, dados[str(user_id)]["mimos"] - valor)
    salvar(dados)


