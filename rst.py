import os
import re
import requests


# ============================================================
# CORES
# ============================================================

RESET = "\033[0m"
CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"


# ============================================================
# HELLO KITTY
# ============================================================

HELLO_KITTY = r"""
⠀⠀    ⠀⠀⢀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⣠⠾⠛⠶⣄⢀⣠⣤⠴⢦⡀⠀⠀⠀⠀
⠀⠀   ⠀ ⢠⡿⠉⠉⠉⠛⠶⠶⠖⠒⠒⣾⠋⠀⢀⣀⣙⣯⡁⠀⠀⠀⣿⠀⠀⠀⠀
⠀⠀⠀    ⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⢸⡏⠀⠀⢯⣼⠋⠉⠙⢶⠞⠛⠻⣆⠀⠀⠀
⠀⠀   ⠀ ⢸⣧⠆⠀⠀⠀⠀⠀⠀⠀⠀⠻⣦⣤⡤⢿⡀⠀⢀⣼⣷⠀⠀⣽⠀⠀⠀
  ⠀  ⠀⠀⣼⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⢏⡉⠁⣠⡾⣇⠀⠀⠀
    ⠀⠀⢰⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠋⠉⠀⢻⡀⠀⠀
   ⣀⣠⣼⣧⣤⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠐⠖⢻⡟⠓⠒
   ⠀⠀⠈⣷⣀⡀⠀⠘⠿⠇⠀⠀⠀⢀⣀⣀⠀⠀⠀⠀⠿⠟⠀⠀⠀⠲⣾⠦⢤⠀
    ⠀⠀⠋⠙⣧⣀⡀⠀⠀⠀⠀⠀⠀⠘⠦⠼⠃⠀⠀⠀⠀⠀⠀⠀⢤⣼⣏⠀⠀⠀
    ⠀⠀⢀⠴⠚⠻⢧⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⠞⠉⠉⠓⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⠛⠶⠶⠶⣶⣤⣴⡶⠶⠶⠟⠛⠉⠀⠀⠀⠀⠀⠀⠀



             HELLO KITTY
"""


# ============================================================
# FUNÇÕES
# ============================================================

def limpar():
    os.system("clear")


def pausar():
    input(f"\n{YELLOW}Pressione ENTER para voltar...{RESET}")


def somente_numeros(valor):
    return re.sub(r"\D", "", valor)


def mostrar_hello_kitty():
    print("\n")
    print(f"{MAGENTA}{HELLO_KITTY}{RESET}")


# ============================================================
# MENU
# ============================================================

def menu():
    limpar()

    mostrar_hello_kitty()

    print(f"{CYAN}[1]{RESET} Consultar CEP")
    print(f"{CYAN}[2]{RESET} Consultar CNPJ")
    print(f"{CYAN}[3]{RESET} Consultar IP")
    print(f"{CYAN}[4]{RESET} Consultar meu IP")
    print(f"{RED}[0]{RESET} Sair")


# ============================================================
# CONSULTA CEP
# ============================================================

def consulta_cep():

    limpar()

    print(f"{MAGENTA}╔══════════════════════════════════════════════╗")
    print("║              CONSULTA DE CEP                 ║")
    print(f"╚══════════════════════════════════════════════╝{RESET}")

    cep = input(f"\n{WHITE}Digite o CEP: {RESET}")

    cep = somente_numeros(cep)

    if len(cep) != 8:
        print(f"\n{RED}CEP inválido. Digite 8 números.{RESET}")
        mostrar_hello_kitty()
        pausar()
        return

    url = f"https://viacep.com.br/ws/{cep}/json/"

    try:

        print(f"\n{YELLOW}Consultando CEP...{RESET}")

        resposta = requests.get(
            url,
            timeout=10
        )

        resposta.raise_for_status()

        dados = resposta.json()

        if dados.get("erro"):
            print(f"\n{RED}CEP não encontrado.{RESET}")
            mostrar_hello_kitty()
            pausar()
            return

        print(f"\n{GREEN}════════════ DADOS DO CEP ════════════{RESET}")

        print(
            f"{GREEN}CEP:{RESET}          "
            f"{dados.get('cep', 'N/A')}"
        )

        print(
            f"{GREEN}Logradouro:{RESET}  "
            f"{dados.get('logradouro', 'N/A')}"
        )

        print(
            f"{GREEN}Complemento:{RESET} "
            f"{dados.get('complemento') or 'N/A'}"
        )

        print(
            f"{GREEN}Bairro:{RESET}      "
            f"{dados.get('bairro', 'N/A')}"
        )

        print(
            f"{GREEN}Cidade:{RESET}      "
            f"{dados.get('localidade', 'N/A')}"
        )

        print(
            f"{GREEN}Estado:{RESET}      "
            f"{dados.get('uf', 'N/A')}"
        )

        print(
            f"{GREEN}IBGE:{RESET}        "
            f"{dados.get('ibge', 'N/A')}"
        )

        print(
            f"{GREEN}GIA:{RESET}         "
            f"{dados.get('gia') or 'N/A'}"
        )

        print(
            f"{GREEN}DDD:{RESET}         "
            f"{dados.get('ddd', 'N/A')}"
        )

        print(
            f"{GREEN}SIAFI:{RESET}       "
            f"{dados.get('siafi', 'N/A')}"
        )

    except requests.exceptions.Timeout:

        print(
            f"\n{RED}"
            "Tempo limite excedido."
            f"{RESET}"
        )

    except requests.exceptions.RequestException:

        print(
            f"\n{RED}"
            "Erro ao acessar a API do CEP."
            f"{RESET}"
        )

    except ValueError:

        print(
            f"\n{RED}"
            "Resposta inválida da API."
            f"{RESET}"
        )

    mostrar_hello_kitty()

    pausar()


# ============================================================
# CONSULTA CNPJ
# ============================================================

def consulta_cnpj():

    limpar()

    print(f"{MAGENTA}╔══════════════════════════════════════════════╗")
    print("║             CONSULTA DE CNPJ                 ║")
    print(f"╚══════════════════════════════════════════════╝{RESET}")

    cnpj = input(f"\n{WHITE}Digite o CNPJ: {RESET}")

    cnpj = somente_numeros(cnpj)

    if len(cnpj) != 14:

        print(
            f"\n{RED}"
            "CNPJ inválido. Digite 14 números."
            f"{RESET}"
        )

        mostrar_hello_kitty()
        pausar()

        return

    url = f"https://receitaws.com.br/v1/cnpj/{cnpj}"

    try:

        print(
            f"\n{YELLOW}"
            "Consultando CNPJ..."
            f"{RESET}"
        )

        resposta = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        resposta.raise_for_status()

        dados = resposta.json()

        if dados.get("status") != "OK":

            print(
                f"\n{RED}"
                f"{dados.get('message', 'CNPJ não encontrado.')}"
                f"{RESET}"
            )

            mostrar_hello_kitty()
            pausar()

            return

        atividade = dados.get(
            "atividade_principal",
            []
        )

        if atividade:

            atividade_principal = atividade[0].get(
                "text",
                "N/A"
            )

        else:

            atividade_principal = "N/A"

        print(
            f"\n{GREEN}"
            "════════════ DADOS DA EMPRESA ════════════"
            f"{RESET}"
        )

        print(
            f"{GREEN}CNPJ:{RESET}             "
            f"{dados.get('cnpj', 'N/A')}"
        )

        print(
            f"{GREEN}Empresa:{RESET}          "
            f"{dados.get('nome', 'N/A')}"
        )

        print(
            f"{GREEN}Nome Fantasia:{RESET}    "
            f"{dados.get('fantasia') or 'N/A'}"
        )

        print(
            f"{GREEN}Situação:{RESET}        "
            f"{dados.get('situacao', 'N/A')}"
        )

        print(
            f"{GREEN}Data Abertura:{RESET}   "
            f"{dados.get('abertura', 'N/A')}"
        )

        print(
            f"{GREEN}Natureza Jurídica:{RESET} "
            f"{dados.get('natureza_juridica', 'N/A')}"
        )

        print(
            f"{GREEN}Capital Social:{RESET}  "
            f"R$ {dados.get('capital_social', 'N/A')}"
        )

        print(
            f"{GREEN}Atividade:{RESET}       "
            f"{atividade_principal}"
        )

        print(
            f"\n{CYAN}"
            "════════════ ENDEREÇO ════════════"
            f"{RESET}"
        )

        print(
            f"{GREEN}Logradouro:{RESET}  "
            f"{dados.get('logradouro', 'N/A')}"
        )

        print(
            f"{GREEN}Número:{RESET}      "
            f"{dados.get('numero', 'N/A')}"
        )

        print(
            f"{GREEN}Complemento:{RESET} "
            f"{dados.get('complemento') or 'N/A'}"
        )

        print(
            f"{GREEN}Bairro:{RESET}      "
            f"{dados.get('bairro', 'N/A')}"
        )

        print(
            f"{GREEN}Município:{RESET}   "
            f"{dados.get('municipio', 'N/A')}"
        )

        print(
            f"{GREEN}UF:{RESET}          "
            f"{dados.get('uf', 'N/A')}"
        )

        print(
            f"{GREEN}CEP:{RESET}         "
            f"{dados.get('cep', 'N/A')}"
        )

        print(
            f"\n{CYAN}"
            "════════════ CONTATO ════════════"
            f"{RESET}"
        )

        print(
            f"{GREEN}Telefone:{RESET}    "
            f"{dados.get('telefone') or 'N/A'}"
        )

        print(
            f"{GREEN}E-mail:{RESET}      "
            f"{dados.get('email') or 'N/A'}"
        )

    except requests.exceptions.Timeout:

        print(
            f"\n{RED}"
            "Tempo limite excedido."
            f"{RESET}"
        )

    except requests.exceptions.RequestException:

        print(
            f"\n{RED}"
            "Erro ao acessar a API do CNPJ."
            f"{RESET}"
        )

    except ValueError:

        print(
            f"\n{RED}"
            "Resposta inválida da API."
            f"{RESET}"
        )

    mostrar_hello_kitty()

    pausar()


# ============================================================
# CONSULTA IP
# ============================================================

def consulta_ip(ip=None):

    limpar()

    print(f"{MAGENTA}╔══════════════════════════════════════════════╗")
    print("║               CONSULTA DE IP                 ║")
    print(f"╚══════════════════════════════════════════════╝{RESET}")

    if not ip:

        ip = input(
            f"\n{WHITE}"
            "Digite o IP (ENTER = seu IP): "
            f"{RESET}"
        ).strip()

    if ip:

        url = f"https://ipwho.is/{ip}"

    else:

        url = "https://ipwho.is/"

    try:

        print(
            f"\n{YELLOW}"
            "Consultando IP..."
            f"{RESET}"
        )

        resposta = requests.get(
            url,
            timeout=10
        )

        resposta.raise_for_status()

        dados = resposta.json()

        if not dados.get("success", False):

            print(
                f"\n{RED}"
                "IP inválido ou não encontrado."
                f"{RESET}"
            )

            mostrar_hello_kitty()
            pausar()

            return

        conexao = dados.get(
            "connection",
            {}
        )

        timezone = dados.get(
            "timezone",
            {}
        )

        localizacao = dados.get(
            "location",
            {}
        )

        print(
            f"\n{GREEN}"
            "════════════ DADOS DO IP ════════════"
            f"{RESET}"
        )

        print(
            f"{GREEN}IP:{RESET}             "
            f"{dados.get('ip', 'N/A')}"
        )

        print(
            f"{GREEN}Tipo:{RESET}           "
            f"{dados.get('type', 'N/A')}"
        )

        print(
            f"{GREEN}País:{RESET}           "
            f"{dados.get('country', 'N/A')}"
        )

        print(
            f"{GREEN}Código País:{RESET}    "
            f"{dados.get('country_code', 'N/A')}"
        )

        print(
            f"{GREEN}Continente:{RESET}     "
            f"{dados.get('continent', 'N/A')}"
        )

        print(
            f"{GREEN}Região:{RESET}         "
            f"{dados.get('region', 'N/A')}"
        )

        print(
            f"{GREEN}Cidade:{RESET}         "
            f"{dados.get('city', 'N/A')}"
        )

        print(
            f"{GREEN}CEP:{RESET}            "
            f"{dados.get('postal', 'N/A')}"
        )

        print(
            f"{GREEN}Capital:{RESET}        "
            f"{dados.get('capital', 'N/A')}"
        )

        print(
            f"\n{CYAN}"
            "════════════ LOCALIZAÇÃO ════════════"
            f"{RESET}"
        )

        print(
            f"{GREEN}Latitude:{RESET}       "
            f"{localizacao.get('latitude', dados.get('latitude', 'N/A'))}"
        )

        print(
            f"{GREEN}Longitude:{RESET}      "
            f"{localizacao.get('longitude', dados.get('longitude', 'N/A'))}"
        )

        print(
            f"{GREEN}Fuso:{RESET}           "
            f"{timezone.get('id', 'N/A')}"
        )

        print(
            f"{GREEN}UTC:{RESET}            "
            f"{timezone.get('utc', 'N/A')}"
        )

        print(
            f"{GREEN}Horário:{RESET}        "
            f"{timezone.get('current_time', 'N/A')}"
        )

        print(
            f"\n{CYAN}"
            "════════════ REDE ════════════"
            f"{RESET}"
        )

        print(
            f"{GREEN}ISP:{RESET}            "
            f"{conexao.get('isp', 'N/A')}"
        )

        print(
            f"{GREEN}Organização:{RESET}    "
            f"{conexao.get('org', 'N/A')}"
        )

        print(
            f"{GREEN}ASN:{RESET}            "
            f"{conexao.get('asn', 'N/A')}"
        )

        print(
            f"{GREEN}Domínio:{RESET}        "
            f"{conexao.get('domain', 'N/A')}"
        )

    except requests.exceptions.Timeout:

        print(
            f"\n{RED}"
            "Tempo limite excedido."
            f"{RESET}"
        )

    except requests.exceptions.RequestException:

        print(
            f"\n{RED}"
            "Erro ao consultar o IP."
            f"{RESET}"
        )

    except ValueError:

        print(
            f"\n{RED}"
            "Resposta inválida da API."
            f"{RESET}"
        )

    mostrar_hello_kitty()

    pausar()


# ============================================================
# MEU IP
# ============================================================

def meu_ip():

    try:

        print(
            f"\n{YELLOW}"
            "Obtendo seu IP público..."
            f"{RESET}"
        )

        resposta = requests.get(
            "https://api.ipify.org?format=json",
            timeout=10
        )

        resposta.raise_for_status()

        dados = resposta.json()

        ip = dados.get("ip")

        if ip:

            consulta_ip(ip)

        else:

            print(
                f"\n{RED}"
                "Não foi possível obter seu IP."
                f"{RESET}"
            )

            mostrar_hello_kitty()
            pausar()

    except requests.exceptions.RequestException:

        print(
            f"\n{RED}"
            "Erro ao obter seu IP."
            f"{RESET}"
        )

        mostrar_hello_kitty()
        pausar()


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

while True:

    menu()

    opcao = input(
        f"\n{CYAN}Escolha uma opção: {RESET}"
    ).strip()

    if opcao == "1":

        consulta_cep()

    elif opcao == "2":

        consulta_cnpj()

    elif opcao == "3":

        consulta_ip()

    elif opcao == "4":

        limpar()
        meu_ip()

    elif opcao == "0":

        limpar()

        print(
            f"\n{MAGENTA}"
            "Até mais! 👋"
            f"{RESET}\n"
        )

        break

    else:

        print(
            f"\n{RED}"
            "Opção inválida."
            f"{RESET}"
        )

        pausar()

dc: ristoteles7 
