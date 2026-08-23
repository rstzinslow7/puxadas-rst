#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║   🎀 Painel Hello Kitty - v2.0 🎀      ║
║   Sistema de consulta - acesso fixo    ║
║   dc: ristoteles7                       ║
╚══════════════════════════════════════════╝

Tudo em um arquivo só.
Abra no nano, rode com python painel.py

Dependências: pip install requests bcrypt cachetools
"""

import os
import re
import sys
import json
import hashlib
import ipaddress
from getpass import getpass
import secrets
import time
import uuid
from datetime import datetime, timedelta
from collections import defaultdict

try:
    import requests
except ImportError:
    print("Instale as dependências:")
    print("  pip install requests bcrypt cachetools")
    sys.exit(1)

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False

try:
    from cachetools import TTLCache
    HAS_CACHE = True
except ImportError:
    HAS_CACHE = False


# ══════════════════════════════════════════════
# CONFIGURAÇÃO (tudo embutido, sem .env)
# ══════════════════════════════════════════════

AUTH_LOG_FILE = "auth.log"
AUDIT_LOG_FILE = "audit.log"
SESSION_SECRET_FILE = "session.secret"

def _load_or_create_secret():
    try:
        if os.path.exists(SESSION_SECRET_FILE):
            with open(SESSION_SECRET_FILE, "r", encoding="utf-8") as f:
                value = f.read().strip()
                if value:
                    return value
        value = secrets.token_hex(32)
        with open(SESSION_SECRET_FILE, "w", encoding="utf-8") as f:
            f.write(value)
        try:
            os.chmod(SESSION_SECRET_FILE, 0o600)
        except OSError:
            pass
        return value
    except OSError:
        return secrets.token_hex(32)

SESSION_SECRET = _load_or_create_secret()
SESSION_EXPIRY = 1800
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 300
RATE_LIMIT_PER_MINUTE = 10
RECEITAWS_API_URL = "https://receitaws.com.br/v1/cnpj"
RECEITAWS_API_TOKEN = ""
BRASIL_API_URL = "https://brasilapi.com.br/api"
DEFAULT_TIMEOUT = 15
MAX_RETRIES = 2
RETRY_DELAY = 1


# ══════════════════════════════════════════════
# CACHE
# ══════════════════════════════════════════════

if HAS_CACHE:
    _cache = TTLCache(maxsize=100, ttl=300)
else:
    _cache = {}


# ══════════════════════════════════════════════
# CORES ANSI
# ══════════════════════════════════════════════

RESET = "\033[0m"
CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
BOLD = "\033[1m"
DIM = "\033[2m"


# ══════════════════════════════════════════════
# HELLO KITTY ASCII
# ══════════════════════════════════════════════

HELLO_KITTY = r"""

⠀⠀    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⣤⣶⢶⣶⣄⠀⣠⣴⣾⠿⠿⣷⣄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⣠⣤⣤⣄⣀⡀⠀⠀⠀⠀⢀⣀⣀⣀⣠⣾⠋⠀⠀⠈⠹⣿⡟⠉⠀⠀⠀⠘⣿⡄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣾⠟⠉⠉⠉⠛⠻⢿⣶⠿⠿⠟⠛⠛⠛⣿⠇⠀⢠⣶⣶⣶⣿⣷⣦⣤⣀⣠⣤⣿⣷⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢸⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⠀⠀⢸⣿⣼⡿⠁⠀⠀⠙⣿⣯⡁⠀⠈⢿⡇⠀⠀⠀⠀
⠀⠀⠀⠀⢹⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣄⠀⠀⢙⣿⣷⡀⠀⠀⢠⣿⣿⣿⡆⠀⣾⡇⠀⠀⠀⠀
⠀⠀⠀⠀⠈⢿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠛⠛⠛⠋⠙⠻⠷⠾⣿⡟⠛⠋⠀⣴⡟⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣾⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⠷⡶⠿⠛⣿⡄⠀⠀⠀⠀
⠀⠀⠀⠀⣸⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣹⣷⣤⣤⣤⡄
⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣄⡀⠀⠀⠀⠘⠋⢹⣿⠀⠀⠀⠀
⠀⣀⣀⣤⣿⣧⣤⡄⠀⠀⠀⢀⣤⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⡷⠀⠀⠀⠀⢠⣼⣿⣤⣤⡤⠀
⠈⠛⠉⠉⠹⣿⠀⠀⠀⠀⠀⠸⣿⡿⠀⠀⠀⠀⠀⢀⣠⡤⣤⡀⠀⠀⠀⠀⠈⠉⠀⠀⠀⠀⠀⢀⣾⠏⠀⠀⠀⠀
⠀⠀⠀⣀⣤⣿⣷⠞⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠷⠤⠼⣃⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢛⣿⡿⢶⣤⣄⠀⠀
⠀⠀⠀⠉⠁⠀⠹⣷⣤⡴⠆⠀⠀⠀⠀⠀⢀⣤⣤⣤⣤⣤⣼⡟⣻⡇⠀⠀⠀⠀⠀⠀⣀⣴⡿⠋⠀⠀⠀⠉⠀⠀
⠀⠀⠀⠀⢀⣠⡾⠟⠛⠿⣶⣤⣤⣤⣄⣰⣿⣍⣀⡀⠀⠈⠙⠳⠿⢷⣦⣀⣠⣤⣶⣿⣟⠉⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠘⠋⠀⠀⠀⣰⡟⠉⠀⠀⠙⣿⣅⣉⣿⣁⣀⣠⣶⡀⠀⠀⠈⣿⡏⠁⠀⠀⠹⣷⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠠⣿⠀⠀⠀⠀⠀⣿⣧⡽⠉⠛⢉⣉⣘⣷⣄⣰⣿⣿⠇⠀⠀⠀⠀⣿⡆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡄⠀⠀⠀⠀⣻⡷⡄⣞⣳⠘⢦⣇⡈⠙⡿⢿⡇⠀⠀⠀⠀⢠⣿⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣴⡟⠉⢿⣦⣄⣠⣴⡿⠛⣡⣌⣿⢳⡞⠧⣿⣀⡙⠚⢿⣦⣄⣤⣴⠟⠙⢿⡄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢰⡿⠀⠀⠀⠈⠉⠉⢹⣧⠈⠳⠞⡉⢻⡷⢦⠸⢭⣧⣤⡿⠋⠉⠉⠀⠀⠀⠈⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣇⠀⠀⠀⠀⠀⠀⠈⣿⣆⠀⢾⣹⠆⠙⢫⣶⣾⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠘⣿⡀⠀⠀⠀⠀⠀⠀⠘⢿⣶⣤⣤⣴⣾⡿⠻⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⢰⡿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠹⣷⣄⠀⠀⠀⠀⠀⢀⣼⣿⣿⡿⠿⠿⣷⣶⣿⣷⡀⠀⠀⠀⠀⠀⢀⣴⡿⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⢷⣦⣤⣤⣴⡿⠋⠁⠀⠀⠀⠀⠀⠀⠈⠙⢿⣦⣤⣀⣤⣴⡿⠛⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀



              painel hello kitty
               dc: ristoteles7
"""


# ══════════════════════════════════════════════
# RBAC - PERFIS E PERMISSÕES
# ══════════════════════════════════════════════

class Role:
    CONSULTA = "CONSULTA"
    OPERADOR = "OPERADOR"
    AUDITOR = "AUDITOR"
    ADMIN = "ADMIN"
    ALL = [CONSULTA, OPERADOR, AUDITOR, ADMIN]

FUNC_PERMISSIONS = {
    "consulta_pessoa":   [Role.CONSULTA, Role.OPERADOR, Role.AUDITOR, Role.ADMIN],
    "auditoria":         [Role.AUDITOR, Role.ADMIN],
    "gerenciar_usuarios": [Role.ADMIN],
}

FIELD_PERMISSIONS = {
    "cpf":             [Role.OPERADOR, Role.AUDITOR, Role.ADMIN],
    "nome":            Role.ALL,
    "nome_mae":        [Role.AUDITOR, Role.ADMIN],
    "data_nascimento": [Role.OPERADOR, Role.AUDITOR, Role.ADMIN],
    "endereco":        [Role.OPERADOR, Role.AUDITOR, Role.ADMIN],
    "telefone":        [Role.AUDITOR, Role.ADMIN],
    "email":           [Role.AUDITOR, Role.ADMIN],
}


# ══════════════════════════════════════════════
# HASH DE SENHA
# ══════════════════════════════════════════════

def hash_password(password: str) -> str:
    if HAS_BCRYPT:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
    return hashlib.sha256(f"{SESSION_SECRET}:{password}".encode()).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    if HAS_BCRYPT and stored_hash.startswith("$2b$"):
        try:
            return bcrypt.checkpw(password.encode(), stored_hash.encode())
        except Exception:
            return False
    return hashlib.sha256(f"{SESSION_SECRET}:{password}".encode()).hexdigest() == stored_hash


# ══════════════════════════════════════════════
# USUÁRIO FIXO / ACESSO SOMENTE PARA CONSULTA
# ══════════════════════════════════════════════

FIXED_USERNAME = "users"
FIXED_ROLE = Role.CONSULTA
PASSWORD_SALT = b"hellokitty-fixed-user-v1"
PASSWORD_HASH = "28fc8fe9865557b05fa03b894346b9af881f42ea190472afbab195022d382ce6a02592233d7b5defb92a84d211bdba986d8114d34ba9cb8042539e47ee61dffe"

def verify_fixed_password(password: str) -> bool:
    try:
        candidate = hashlib.scrypt(
            password.encode("utf-8"),
            salt=PASSWORD_SALT,
            n=2**14,
            r=8,
            p=1,
            dklen=64,
        ).hex()
        return secrets.compare_digest(candidate, PASSWORD_HASH)
    except Exception:
        return False

def _load_users() -> dict:
    # Não existe banco de usuários editável pelo usuário.
    return {
        FIXED_USERNAME: {
            "password_hash": PASSWORD_HASH,
            "role": FIXED_ROLE,
            "active": True,
            "created": "fixed",
            "login_attempts": 0,
            "locked_until": 0,
        }
    }

def _save_users(users: dict):
    # Bloqueado por projeto: não grava nem altera usuários localmente.
    return None

def create_user(username: str, password: str, role: str, creator: str) -> tuple:
    return False, "Criação de usuários está desativada."

def deactivate_user(username: str, admin: str) -> tuple:
    return False, "Desativação de usuários está desativada."

def list_users(admin: str) -> list:
    return [{
        "username": FIXED_USERNAME,
        "role": FIXED_ROLE,
        "active": True,
        "created": "fixed",
    }]

# ══════════════════════════════════════════════
# RATE LIMITING
# ══════════════════════════════════════════════

_rate_limits: dict = defaultdict(list)


def check_rate_limit(username: str) -> bool:
    now = time.time()
    _rate_limits[username] = [t for t in _rate_limits[username] if now - t < 60]
    if len(_rate_limits[username]) >= RATE_LIMIT_PER_MINUTE:
        return False
    _rate_limits[username].append(now)
    return True


def get_rate_limit_remaining(username: str) -> int:
    now = time.time()
    _rate_limits[username] = [t for t in _rate_limits[username] if now - t < 60]
    return max(0, RATE_LIMIT_PER_MINUTE - len(_rate_limits[username]))


# ══════════════════════════════════════════════
# LOG DE AUTENTICAÇÃO
# ══════════════════════════════════════════════

def _log_auth(event: str, username: str, detail: str = "", success: bool = False):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event,
        "username": username,
        "success": success,
        "detail": detail,
    }
    try:
        with open(AUTH_LOG_FILE, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except IOError:
        pass


# ══════════════════════════════════════════════
# SESSÃO
# ══════════════════════════════════════════════

class Session:
    def __init__(self):
        self.username = ""
        self.role = ""
        self.token = ""
        self.created_at = 0
        self.expires_at = 0

    def is_valid(self) -> bool:
        return bool(self.token) and time.time() < self.expires_at

    def refresh(self):
        self.expires_at = time.time() + SESSION_EXPIRY

    def clear(self):
        self.username = ""
        self.role = ""
        self.token = ""
        self.created_at = 0
        self.expires_at = 0


# ══════════════════════════════════════════════
# LOGIN / LOGOUT
# ══════════════════════════════════════════════

def login(username: str, password: str, session: Session) -> tuple:
    username = username.strip()

    if username != FIXED_USERNAME:
        _log_auth("LOGIN_FAIL", username, "usuário não autorizado")
        return False, "Usuário ou senha inválidos.", session

    if not verify_fixed_password(password):
        _log_auth("LOGIN_FAIL", username, "senha incorreta")
        return False, "Usuário ou senha inválidos.", session

    session.username = FIXED_USERNAME
    session.role = FIXED_ROLE
    session.token = secrets.token_hex(32)
    session.created_at = time.time()
    session.refresh()

    _log_auth("LOGIN_OK", FIXED_USERNAME, "acesso somente consulta", success=True)
    return True, f"Bem-vindo, {FIXED_USERNAME}!", session


def logout(session: Session):
    _log_auth("LOGOUT", session.username, "")
    session.clear()


# ══════════════════════════════════════════════
# PERMISSÕES
# ══════════════════════════════════════════════

def has_permission(role: str, func: str) -> bool:
    allowed = FUNC_PERMISSIONS.get(func, [])
    return role in allowed


def can_see_field(role: str, field: str) -> bool:
    allowed = FIELD_PERMISSIONS.get(field, [])
    return role in allowed


# ══════════════════════════════════════════════
# MASCARAMENTO
# ══════════════════════════════════════════════

def mask_cpf(cpf: str) -> str:
    d = ""
    for c in str(cpf):
        if c.isdigit():
            d += c
    if len(d) != 11:
        return "***.***.***-**"
    return f"***.***.***-{d[-2:]}"


def mask_phone(phone: str) -> str:
    d = ""
    for c in str(phone):
        if c.isdigit():
            d += c
    if len(d) >= 4:
        return f"(**) *****-{d[-4:]}"
    return "(**) ****-****"


def mask_email(email: str) -> str:
    if "@" not in str(email):
        return "***@***.***"
    local, domain = email.split("@", 1)
    if len(local) <= 1:
        return f"*@{domain}"
    return f"{local[0]}{'*' * min(5, len(local) - 1)}@{domain}"


def mask_date(date_str: str) -> str:
    if not date_str or date_str == "N/A":
        return "N/A"
    return "**/**/****"


def mask_name(name: str) -> str:
    if not name or name == "N/A":
        return "N/A"
    parts = name.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{'*' * (len(parts[0]) - 1)} {parts[-1][0]}."
    return f"{name[0]}{'*' * (len(name) - 1)}"


def apply_mask(field: str, value: str, role: str) -> str:
    if not value or value == "N/A":
        return value
    if can_see_field(role, field):
        return value
    maskers = {
        "cpf": mask_cpf,
        "nome": mask_name,
        "nome_mae": mask_name,
        "data_nascimento": mask_date,
        "telefone": mask_phone,
        "email": mask_email,
    }
    masker = maskers.get(field)
    if masker:
        return masker(value)
    return "***"


# ══════════════════════════════════════════════
# CRUD USUÁRIOS
# ══════════════════════════════════════════════

def create_user(username: str, password: str, role: str, creator: str) -> tuple:
    if len(password) < 8:
        return False, "Senha deve ter no mínimo 8 caracteres."
    if role not in Role.ALL:
        return False, f"Perfil inválido. Use: {', '.join(Role.ALL)}"
    users = _load_users()
    if username in users:
        return False, "Usuário já existe."
    users[username] = {
        "password_hash": hash_password(password),
        "role": role,
        "active": True,
        "created": datetime.now().isoformat(),
        "login_attempts": 0,
        "locked_until": 0,
    }
    _save_users(users)
    _log_auth("USER_CREATED", creator, f"criou usuário {username} ({role})")
    return True, f"Usuário {username} ({role}) criado com sucesso!"


def deactivate_user(username: str, admin: str) -> tuple:
    users = _load_users()
    if username not in users:
        return False, "Usuário não existe."
    if username == admin:
        return False, "Não pode desativar a si mesmo."
    users[username]["active"] = False
    _save_users(users)
    _log_auth("USER_DEACTIVATED", admin, f"desativou {username}")
    return True, f"Usuário {username} desativado."


def list_users(admin: str) -> list:
    users = _load_users()
    result = []
    for uname, data in users.items():
        result.append({
            "username": uname,
            "role": data.get("role", "N/A"),
            "active": data.get("active", True),
            "created": data.get("created", "N/A"),
        })
    return result


# ══════════════════════════════════════════════
# AUDITORIA
# ══════════════════════════════════════════════

def log_audit(
    username: str,
    query_type: str,
    identifier_masked: str,
    purpose: str,
    api_source: str,
    result_status: str,
    http_status: int = 0,
    details: str = "",
) -> str:
    req_id = str(uuid.uuid4())[:8].upper()
    entry = {
        "request_id": req_id,
        "timestamp": datetime.now().isoformat(),
        "username": username,
        "query_type": query_type,
        "identifier": identifier_masked,
        "purpose": purpose,
        "api_source": api_source,
        "result_status": result_status,
        "http_status": http_status,
        "details": details,
    }
    try:
        with open(AUDIT_LOG_FILE, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except IOError:
        pass
    return req_id


def read_audit_log(limit: int = 50) -> list:
    if not os.path.exists(AUDIT_LOG_FILE):
        return []
    entries = []
    try:
        with open(AUDIT_LOG_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except IOError:
        return []
    return entries[-limit:]


def get_audit_stats() -> dict:
    entries = read_audit_log(limit=10000)
    by_type = {}
    by_user = {}
    by_status = {}
    for e in entries:
        qt = e.get("query_type", "?")
        by_type[qt] = by_type.get(qt, 0) + 1
        u = e.get("username", "?")
        by_user[u] = by_user.get(u, 0) + 1
        s = e.get("result_status", "?")
        by_status[s] = by_status.get(s, 0) + 1
    return {
        "total_queries": len(entries),
        "by_type": by_type,
        "by_user": by_user,
        "by_status": by_status,
    }


# ══════════════════════════════════════════════
# CLIENTE HTTP SEGURO
# ══════════════════════════════════════════════

from typing import Optional, Tuple


def _make_request(
    url: str,
    method: str = "GET",
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
    json_data: Optional[dict] = None,
    timeout: int = DEFAULT_TIMEOUT,
    use_cache: bool = True,
    use_bearer: bool = False,
) -> Tuple[Optional[dict], int, str]:
    if not url.startswith("https://"):
        return None, 0, "Erro de segurança: HTTPS obrigatório."

    if use_cache and HAS_CACHE and method == "GET":
        cached = _cache.get(url)
        if cached:
            return cached, 200, ""

    req_headers = {"User-Agent": "PainelHelloKitty/2.0"}
    if headers:
        req_headers.update(headers)
    if use_bearer and RECEITAWS_API_TOKEN:
        req_headers["Authorization"] = f"Bearer {RECEITAWS_API_TOKEN}"

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.request(
                method=method, url=url, headers=req_headers,
                params=params, json=json_data, timeout=timeout,
            )
            status = response.status_code

            if status == 200:
                try:
                    data = response.json()
                except ValueError:
                    return None, status, "Resposta não é JSON válido."
                if use_cache and HAS_CACHE and method == "GET":
                    _cache[url] = data
                return data, status, ""

            elif status == 400:
                return None, status, "Requisição inválida (400). Verifique os parâmetros."
            elif status == 401:
                return None, status, "Não autorizado (401). Verifique as credenciais da API."
            elif status == 403:
                return None, status, "Acesso proibido (403)."
            elif status == 404:
                return None, status, "Recurso não encontrado (404)."
            elif status == 429:
                retry_after = response.headers.get("Retry-After", str(RETRY_DELAY * 5))
                return None, status, f"Rate limit excedido (429). Tente em {retry_after}s."
            elif status in (500, 502, 503):
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    continue
                return None, status, f"Erro do servidor ({status}). Tente mais tarde."
            else:
                return None, status, f"Erro HTTP {status}."

        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return None, 0, "Tempo limite excedido."
        except requests.exceptions.ConnectionError:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return None, 0, "Erro de conexão. Verifique sua internet."
        except requests.exceptions.RequestException:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue

    return None, 0, f"Erro após {MAX_RETRIES + 1} tentativas."


# ══════════════════════════════════════════════
# APIs PÚBLICAS OFICIAIS
# ══════════════════════════════════════════════

def consultar_cpf_brasilapi(cpf: str) -> Tuple[Optional[dict], int, str]:
    digits = "".join(c for c in cpf if c.isdigit())
    if len(digits) != 11:
        return None, 0, "CPF deve conter 11 dígitos."
    url = f"https://brasilapi.com.br/api/cpf/v1/{digits}"
    data, status, error = _make_request(url, timeout=DEFAULT_TIMEOUT, use_cache=False, use_bearer=False)
    if error:
        return None, status, error
    if not isinstance(data, dict):
        return None, status, "Resposta inválida da API."
    return data, status, ""


def consultar_cnpj_receitaws(cnpj: str) -> Tuple[Optional[dict], int, str]:
    # Mantém o nome da função por compatibilidade.
    digits = "".join(c for c in cnpj if c.isdigit())

    if len(digits) != 14:
        return None, 0, "CNPJ deve conter 14 dígitos."

    url = f"https://brasilapi.com.br/api/cnpj/v1/{digits}"

    data, status, error = _make_request(
        url,
        timeout=DEFAULT_TIMEOUT,
        use_cache=True
    )

    if error:
        return None, status, error

    if not isinstance(data, dict):
        return None, status, "Resposta inválida da API."

    return data, status, ""


def consultar_cep_viacep(cep: str) -> Tuple[Optional[dict], int, str]:
    # Endpoint atual da BrasilAPI, com fallback de providers.
    digits = "".join(c for c in cep if c.isdigit())
    if len(digits) != 8:
        return None, 0, "CEP deve conter 8 dígitos."
    url = f"https://brasilapi.com.br/api/cep/v1/{digits}"
    data, status, error = _make_request(url, timeout=10)
    if error:
        return None, status, error
    if not isinstance(data, dict):
        return None, status, "Resposta inválida da API."
    if data.get("erro"):
        return None, status, "CEP não encontrado."
    # Normaliza o formato para o restante do painel.
    return {
        "cep": data.get("cep", digits),
        "logradouro": data.get("street", data.get("logradouro", "")),
        "complemento": data.get("complemento", ""),
        "bairro": data.get("neighborhood", data.get("bairro", "")),
        "localidade": data.get("city", data.get("localidade", "")),
        "uf": data.get("state", data.get("uf", "")),
        "ibge": (data.get("ibge") or {}).get("city") if isinstance(data.get("ibge"), dict) else data.get("ibge", ""),
        "gia": data.get("gia", ""),
        "ddd": data.get("ddd", ""),
        "siafi": data.get("siafi", ""),
    }, status, ""


def consultar_ip_ipwhois(ip: str) -> Tuple[Optional[dict], int, str]:
    if ip:
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            return None, 0, "IP inválido."
    url = f"https://ipwho.is/{ip}" if ip else "https://ipwho.is/"
    data, status, error = _make_request(url, timeout=10)
    if error:
        return None, status, error
    if isinstance(data, dict) and not data.get("success", False):
        return None, status, "IP inválido ou não encontrado."
    return data, status, ""


def consultar_meu_ip() -> Tuple[Optional[str], int, str]:
    url = "https://api.ipify.org?format=json"
    data, status, error = _make_request(url, timeout=10)
    if error:
        return None, status, error
    if isinstance(data, dict):
        return data.get("ip"), status, ""
    return None, status, "Resposta inválida."


# ══════════════════════════════════════════════
# UTILITÁRIOS DE TELA
# ══════════════════════════════════════════════

def limpar():
    os.system("clear")


def pausar():
    input(f"\n{YELLOW}Pressione ENTER para voltar...{RESET}")


def somente_numeros(valor):
    return re.sub(r"\D", "", valor)


def mostrar_hello_kitty():
    print("\n")
    print(f"{MAGENTA}{HELLO_KITTY}{RESET}")


def formatar_cpf(cpf: str) -> str:
    d = somente_numeros(cpf)
    if len(d) != 11:
        return cpf
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"


def formatar_cnpj(cnpj: str) -> str:
    d = somente_numeros(cnpj)
    if len(d) != 14:
        return cnpj
    return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"


def cabecalho(titulo: str):
    print(f"{MAGENTA}╔{'═' * 48}╗")
    print(f"║{titulo:^48}║")
    print(f"╚{'═' * 48}╝{RESET}")


def secao(titulo: str):
    print(f"\n{CYAN}════════════ {titulo} ════════════{RESET}")


# ══════════════════════════════════════════════
# SESSÃO GLOBAL
# ══════════════════════════════════════════════

session = Session()


# ══════════════════════════════════════════════
# TELA DE LOGIN
# ══════════════════════════════════════════════

def tela_login():
    limpar()
    mostrar_hello_kitty()

    print(f"{BOLD}{MAGENTA}════════════ LOGIN ════════════{RESET}")
    print()

    username = input(f"{WHITE}Usuário: {RESET}").strip()
    if not username:
        return False

    try:
        password = getpass(f"{WHITE}Senha: {RESET}").strip()
    except (EOFError, KeyboardInterrupt):
        return False
    if not password:
        return False

    print()
    success, message, session_ref = login(username, password, session)

    if success:
        print(f"{GREEN}{message}{RESET}")
        print(f"{DIM}Perfil: {session.role}{RESET}")
        rl = get_rate_limit_remaining(session.username)
        print(f"{DIM}Rate limit: {rl}/{RATE_LIMIT_PER_MINUTE} consultas/min{RESET}")
        pausar()
        return True
    else:
        print(f"{RED}{message}{RESET}")
        pausar()
        return False


# ══════════════════════════════════════════════
# MENU PRINCIPAL
# ══════════════════════════════════════════════

def menu():
    limpar()
    mostrar_hello_kitty()

    if session.is_valid():
        session.refresh()
        print(f"{DIM}Sessão: {session.username} ({session.role}){RESET}")
        print(f"{DIM}Consultas restantes: {get_rate_limit_remaining(session.username)}/min{RESET}")
        print()

    print(f"{CYAN}[1]{RESET} Consultar CEP")
    print(f"{CYAN}[2]{RESET} Consultar CNPJ")
    print(f"{CYAN}[3]{RESET} Consultar IP")
    print(f"{CYAN}[4]{RESET} Consultar meu IP")

    if session.is_valid() and has_permission(session.role, "consulta_pessoa"):
        print(f"{CYAN}[5]{RESET} Consultar Pessoa")

    print(f"{CYAN}[8]{RESET} Trocar Usuário")
    print(f"{RED}[0]{RESET} Sair")


# ══════════════════════════════════════════════
# CONSULTA DE PESSOA
# ══════════════════════════════════════════════

def consulta_pessoa():
    if not session.is_valid():
        print(f"\n{RED}Sessão expirada. Faça login novamente.{RESET}")
        pausar()
        return

    if not has_permission(session.role, "consulta_pessoa"):
        print(f"\n{RED}Permissão negada.{RESET}")
        pausar()
        return

    if not check_rate_limit(session.username):
        print(f"\n{RED}Rate limit excedido. Aguarde um minuto.{RESET}")
        pausar()
        return

    limpar()
    cabecalho("CONSULTA DE PESSOA")

    nome = input(f"\n{WHITE}Nome completo (ENTER para pular): {RESET}").strip()
    cpf_input = input(f"{WHITE}CPF (opcional, para confirmação): {RESET}").strip()
    finalidade = input(f"{WHITE}Finalidade da consulta: {RESET}").strip()

    if not finalidade:
        print(f"\n{RED}Finalidade é obrigatória para registro de auditoria.{RESET}")
        mostrar_hello_kitty()
        pausar()
        return

    if cpf_input:
        cpf_digits = somente_numeros(cpf_input)
        if len(cpf_digits) != 11:
            print(f"\n{RED}CPF inválido. Digite 11 números.{RESET}")
            mostrar_hello_kitty()
            pausar()
            return

        print(f"\n{YELLOW}Consultando situação cadastral do CPF...{RESET}")

        dados_cpf, status_cpf, erro_cpf = consultar_cpf_brasilapi(cpf_digits)

        cpf_masked = mask_cpf(formatar_cpf(cpf_digits))

        req_id = log_audit(
            username=session.username,
            query_type="CPF",
            identifier_masked=cpf_masked,
            purpose=finalidade,
            api_source="Brasil API - CPF",
            result_status="OK" if dados_cpf else "ERRO",
            http_status=status_cpf,
            details=erro_cpf if erro_cpf else "",
        )

        if erro_cpf:
            print(f"\n{RED}Erro: {erro_cpf}{RESET}")
            print(f"\n{MAGENTA}════════════ RESULTADO ════════════{RESET}")
            print(f"{GREEN}Fonte:{RESET}        Brasil API - CPF")
            print(f"{GREEN}Consulta:{RESET}     {'autorizada' if status_cpf not in (401, 403) else 'denegada'}")
            print(f"{GREEN}Req ID:{RESET}       {req_id}")
            agora = datetime.now().strftime('%d/%m/%Y %H:%M')
            print(f"{GREEN}Data:{RESET}         {agora}")
            print(f"{RED}Status:{RESET}       ERRO")
            mostrar_hello_kitty()
            pausar()
            return

        print(f"\n{GREEN}════════════ CONSULTA DE PESSOA ════════════{RESET}")

        nome_api = dados_cpf.get("nome", "N/A")
        nome_display = apply_mask("nome", nome_api or nome, session.role)
        print(f"{GREEN}Nome:{RESET}          {nome_display}")

        cpf_display = formatar_cpf(cpf_digits)
        if not can_see_field(session.role, "cpf"):
            cpf_display = mask_cpf(cpf_digits)
        print(f"{GREEN}CPF:{RESET}           {cpf_display}")

        situacao = dados_cpf.get("situacao", "N/A")
        print(f"{GREEN}Situação:{RESET}      {situacao}")

        data_nasc = dados_cpf.get("data_nascimento", "N/A")
        data_display = apply_mask("data_nascimento", data_nasc, session.role)
        print(f"{GREEN}Nascimento:{RESET}    {data_display}")

        data_insc = dados_cpf.get("data_inscricao", "N/A")
        print(f"{GREEN}Inscrição:{RESET}     {data_insc}")

        for campo_api, campo_perm, label in [
            ("nome_mae", "nome_mae", "Nome da Mãe"),
            ("endereco", "endereco", "Endereço"),
            ("telefone", "telefone", "Telefone"),
            ("email", "email", "E-mail"),
        ]:
            valor = dados_cpf.get(campo_api, "N/A")
            if valor and valor != "N/A":
                valor_display = apply_mask(campo_perm, valor, session.role)
                print(f"{GREEN}{label}:{RESET}  {valor_display}")

        print(f"\n{MAGENTA}════════════ RESULTADO ════════════{RESET}")
        print(f"{GREEN}Fonte:{RESET}        Brasil API - CPF")
        print(f"{GREEN}Consulta:{RESET}     autorizada")
        print(f"{GREEN}Req ID:{RESET}       {req_id}")
        agora = datetime.now().strftime('%d/%m/%Y %H:%M')
        print(f"{GREEN}Data:{RESET}         {agora}")

        mostrar_hello_kitty()
        pausar()
        return

    if nome:
        print(f"\n{YELLOW}Consultando...{RESET}")

        nome_masked = f"{nome[0]}{'*' * (len(nome)-2)} {nome.split()[-1][0]}." if len(nome) > 3 else "***"

        req_id = log_audit(
            username=session.username,
            query_type="NOME",
            identifier_masked=nome_masked,
            purpose=finalidade,
            api_source="Interno - Busca por nome",
            result_status="PARCIAL",
            http_status=200,
            details="Consulta por nome requer CPF para resultado completo",
        )

        print(f"\n{GREEN}════════════ CONSULTA DE PESSOA ════════════{RESET}")
        print(f"{GREEN}Nome:{RESET}          {nome}")
        print(f"\n{YELLOW}Consulta por nome requer CPF para dados da Receita Federal.{RESET}")
        print(f"{YELLOW}Informe o CPF para verificação completa.{RESET}")

        print(f"\n{MAGENTA}════════════ RESULTADO ════════════{RESET}")
        print(f"{GREEN}Fonte:{RESET}        Consulta local")
        print(f"{GREEN}Consulta:{RESET}     parcial")
        print(f"{GREEN}Req ID:{RESET}       {req_id}")
        agora = datetime.now().strftime('%d/%m/%Y %H:%M')
        print(f"{GREEN}Data:{RESET}         {agora}")

        mostrar_hello_kitty()
        pausar()
        return

    print(f"\n{RED}Informe ao menos um nome ou CPF.{RESET}")
    mostrar_hello_kitty()
    pausar()


# ══════════════════════════════════════════════
# CONSULTA CEP
# ══════════════════════════════════════════════

def consulta_cep():
    if not session.is_valid():
        print(f"\n{RED}Sessão expirada. Faça login novamente.{RESET}")
        pausar()
        return

    if not check_rate_limit(session.username):
        print(f"\n{RED}Rate limit excedido. Aguarde.{RESET}")
        pausar()
        return

    limpar()
    cabecalho("CONSULTA DE CEP")

    cep = input(f"\n{WHITE}Digite o CEP: {RESET}")
    cep = somente_numeros(cep)

    if len(cep) != 8:
        print(f"\n{RED}CEP inválido. Digite 8 números.{RESET}")
        mostrar_hello_kitty()
        pausar()
        return

    print(f"\n{YELLOW}Consultando CEP...{RESET}")

    dados, status, erro = consultar_cep_viacep(cep)

    log_audit(
        username=session.username,
        query_type="CEP",
        identifier_masked=f"{cep[:5]}-***",
        purpose="Consulta de CEP",
        api_source="ViaCEP",
        result_status="OK" if dados else "ERRO",
        http_status=status,
        details=erro if erro else "",
    )

    if erro:
        print(f"\n{RED}{erro}{RESET}")
        mostrar_hello_kitty()
        pausar()
        return

    secao("DADOS DO CEP")

    for label, valor in [
        ("CEP", dados.get("cep", "N/A")),
        ("Logradouro", dados.get("logradouro", "N/A")),
        ("Complemento", dados.get("complemento") or "N/A"),
        ("Bairro", dados.get("bairro", "N/A")),
        ("Cidade", dados.get("localidade", "N/A")),
        ("Estado", dados.get("uf", "N/A")),
        ("IBGE", dados.get("ibge", "N/A")),
        ("GIA", dados.get("gia") or "N/A"),
        ("DDD", dados.get("ddd", "N/A")),
        ("SIAFI", dados.get("siafi", "N/A")),
    ]:
        esp = max(1, 12 - len(label))
        print(f"{GREEN}{label}:{RESET}{' ' * esp}{valor}")

    mostrar_hello_kitty()
    pausar()


# ══════════════════════════════════════════════
# CONSULTA CNPJ
# ══════════════════════════════════════════════

def consulta_cnpj():
    if not session.is_valid():
        print(f"\n{RED}Sessão expirada. Faça login novamente.{RESET}")
        pausar()
        return

    if not check_rate_limit(session.username):
        print(f"\n{RED}Rate limit excedido. Aguarde.{RESET}")
        pausar()
        return

    limpar()
    cabecalho("CONSULTA DE CNPJ")

    cnpj = input(f"\n{WHITE}Digite o CNPJ: {RESET}")
    cnpj = somente_numeros(cnpj)

    if len(cnpj) != 14:
        print(f"\n{RED}CNPJ inválido. Digite 14 números.{RESET}")
        mostrar_hello_kitty()
        pausar()
        return

    print(f"\n{YELLOW}Consultando CNPJ...{RESET}")

    dados, status, erro = consultar_cnpj_receitaws(cnpj)

    cnpj_masked = f"{cnpj[:2]}.***.***/****-{cnpj[-2:]}"
    log_audit(
        username=session.username,
        query_type="CNPJ",
        identifier_masked=cnpj_masked,
        purpose="Consulta de CNPJ",
        api_source="ReceitaWS",
        result_status="OK" if dados else "ERRO",
        http_status=status,
        details=erro if erro else "",
    )

    if erro:
        print(f"\n{RED}{erro}{RESET}")
        mostrar_hello_kitty()
        pausar()
        return

    atividade = dados.get("atividade_principal", [])
    atividade_principal = atividade[0].get("text", "N/A") if atividade else "N/A"

    secao("DADOS DA EMPRESA")

    for label, valor in [
        ("CNPJ", dados.get("cnpj", "N/A")),
        ("Empresa", dados.get("nome", "N/A")),
        ("Nome Fantasia", dados.get("fantasia") or "N/A"),
        ("Situação", dados.get("situacao", "N/A")),
        ("Data Abertura", dados.get("abertura", "N/A")),
        ("Natureza Jurídica", dados.get("natureza_juridica", "N/A")),
        ("Capital Social", f"R$ {dados.get('capital_social', 'N/A')}"),
        ("Atividade", atividade_principal),
    ]:
        esp = max(1, 14 - len(label))
        print(f"{GREEN}{label}:{RESET}{' ' * esp}{valor}")

    secao("ENDEREÇO")

    for label, valor in [
        ("Logradouro", dados.get("logradouro", "N/A")),
        ("Número", dados.get("numero", "N/A")),
        ("Complemento", dados.get("complemento") or "N/A"),
        ("Bairro", dados.get("bairro", "N/A")),
        ("Município", dados.get("municipio", "N/A")),
        ("UF", dados.get("uf", "N/A")),
        ("CEP", dados.get("cep", "N/A")),
    ]:
        esp = max(1, 12 - len(label))
        print(f"{GREEN}{label}:{RESET}{' ' * esp}{valor}")

    secao("CONTATO")

    for label, valor in [
        ("Telefone", dados.get("telefone") or "N/A"),
        ("E-mail", dados.get("email") or "N/A"),
    ]:
        esp = max(1, 10 - len(label))
        print(f"{GREEN}{label}:{RESET}{' ' * esp}{valor}")

    mostrar_hello_kitty()
    pausar()


# ══════════════════════════════════════════════
# CONSULTA IP
# ══════════════════════════════════════════════

def consulta_ip(ip=None):
    if not session.is_valid():
        print(f"\n{RED}Sessão expirada. Faça login novamente.{RESET}")
        pausar()
        return

    if not check_rate_limit(session.username):
        print(f"\n{RED}Rate limit excedido. Aguarde.{RESET}")
        pausar()
        return

    limpar()
    cabecalho("CONSULTA DE IP")

    if not ip:
        ip = input(f"\n{WHITE}Digite o IP (ENTER = seu IP): {RESET}").strip()

    print(f"\n{YELLOW}Consultando IP...{RESET}")

    dados, status, erro = consultar_ip_ipwhois(ip)

    ip_masked = f"{ip[:3] if ip else '???'}.*.*.*" if ip else "meu_ip"
    log_audit(
        username=session.username,
        query_type="IP",
        identifier_masked=ip_masked,
        purpose="Consulta de IP",
        api_source="ipwho.is",
        result_status="OK" if dados else "ERRO",
        http_status=status,
        details=erro if erro else "",
    )

    if erro:
        print(f"\n{RED}{erro}{RESET}")
        mostrar_hello_kitty()
        pausar()
        return

    conexao = dados.get("connection", {})
    timezone = dados.get("timezone", {})
    localizacao = dados.get("location", {})

    secao("DADOS DO IP")

    for label, valor in [
        ("IP", dados.get("ip", "N/A")),
        ("Tipo", dados.get("type", "N/A")),
        ("País", dados.get("country", "N/A")),
        ("Código País", dados.get("country_code", "N/A")),
        ("Continente", dados.get("continent", "N/A")),
        ("Região", dados.get("region", "N/A")),
        ("Cidade", dados.get("city", "N/A")),
        ("CEP", dados.get("postal", "N/A")),
        ("Capital", dados.get("capital", "N/A")),
    ]:
        esp = max(1, 12 - len(label))
        print(f"{GREEN}{label}:{RESET}{' ' * esp}{valor}")

    secao("LOCALIZAÇÃO")

    for label, valor in [
        ("Latitude", localizacao.get("latitude", dados.get("latitude", "N/A"))),
        ("Longitude", localizacao.get("longitude", dados.get("longitude", "N/A"))),
        ("Fuso", timezone.get("id", "N/A")),
        ("UTC", timezone.get("utc", "N/A")),
        ("Horário", timezone.get("current_time", "N/A")),
    ]:
        esp = max(1, 10 - len(label))
        print(f"{GREEN}{label}:{RESET}{' ' * esp}{valor}")

    secao("REDE")

    for label, valor in [
        ("ISP", conexao.get("isp", "N/A")),
        ("Organização", conexao.get("org", "N/A")),
        ("ASN", conexao.get("asn", "N/A")),
        ("Domínio", conexao.get("domain", "N/A")),
    ]:
        esp = max(1, 12 - len(label))
        print(f"{GREEN}{label}:{RESET}{' ' * esp}{valor}")

    mostrar_hello_kitty()
    pausar()


# ══════════════════════════════════════════════
# MEU IP
# ══════════════════════════════════════════════

def meu_ip():
    if not session.is_valid():
        print(f"\n{RED}Sessão expirada. Faça login novamente.{RESET}")
        pausar()
        return

    try:
        print(f"\n{YELLOW}Obtendo seu IP público...{RESET}")
        ip, status, erro = consultar_meu_ip()
        if erro or not ip:
            print(f"\n{RED}{erro or 'Não foi possível obter seu IP.'}{RESET}")
            mostrar_hello_kitty()
            pausar()
            return
        consulta_ip(ip)
    except Exception:
        print(f"\n{RED}Erro ao obter seu IP.{RESET}")
        mostrar_hello_kitty()
        pausar()


# ══════════════════════════════════════════════
# AUDITORIA
# ══════════════════════════════════════════════

def tela_auditoria():
    return
    if not session.is_valid():
        print(f"\n{RED}Sessão expirada. Faça login novamente.{RESET}")
        pausar()
        return

    if not has_permission(session.role, "auditoria"):
        print(f"\n{RED}Permissão negada. Apenas AUDITOR ou ADMIN.{RESET}")
        pausar()
        return

    limpar()
    cabecalho("AUDITORIA")

    print(f"\n{CYAN}[1]{RESET} Ver consultas recentes")
    print(f"{CYAN}[2]{RESET} Estatísticas")
    print(f"{CYAN}[0]{RESET} Voltar")

    opcao = input(f"\n{WHITE}Escolha: {RESET}").strip()

    if opcao == "1":
        limpar()
        cabecalho("CONSULTAS RECENTES")
        entries = read_audit_log(limit=30)
        if not entries:
            print(f"\n{YELLOW}Nenhum registro encontrado.{RESET}")
        else:
            for i, entry in enumerate(entries, 1):
                print(f"\n{MAGENTA}--- Registro #{i} ---{RESET}")
                print(f"{GREEN}Req ID:{RESET}       {entry.get('request_id', 'N/A')}")
                print(f"{GREEN}Data/Hora:{RESET}    {entry.get('timestamp', 'N/A')}")
                print(f"{GREEN}Usuário:{RESET}      {entry.get('username', 'N/A')}")
                print(f"{GREEN}Tipo:{RESET}         {entry.get('query_type', 'N/A')}")
                print(f"{GREEN}Identif.:{RESET}     {entry.get('identifier', 'N/A')}")
                print(f"{GREEN}Finalidade:{RESET}   {entry.get('purpose', 'N/A')}")
                print(f"{GREEN}API:{RESET}          {entry.get('api_source', 'N/A')}")
                print(f"{GREEN}Resultado:{RESET}    {entry.get('result_status', 'N/A')}")
                print(f"{GREEN}HTTP Status:{RESET}  {entry.get('http_status', 'N/A')}")
                det = entry.get('details', '')
                if det:
                    print(f"{GREEN}Detalhes:{RESET}     {det}")

    elif opcao == "2":
        limpar()
        cabecalho("ESTATÍSTICAS")
        stats = get_audit_stats()
        print(f"\n{GREEN}Total de consultas:{RESET} {stats.get('total_queries', 0)}")
        print(f"\n{CYAN}Por tipo:{RESET}")
        for tipo, count in stats.get("by_type", {}).items():
            print(f"  {tipo}: {count}")
        print(f"\n{CYAN}Por usuário:{RESET}")
        for user, count in stats.get("by_user", {}).items():
            print(f"  {user}: {count}")
        print(f"\n{CYAN}Por status:{RESET}")
        for status, count in stats.get("by_status", {}).items():
            print(f"  {status}: {count}")

    mostrar_hello_kitty()
    pausar()


# ══════════════════════════════════════════════
# GERENCIAR USUÁRIOS
# ══════════════════════════════════════════════

def tela_gerenciar_usuarios():
    return
    if not session.is_valid():
        print(f"\n{RED}Sessão expirada. Faça login novamente.{RESET}")
        pausar()
        return

    if not has_permission(session.role, "gerenciar_usuarios"):
        print(f"\n{RED}Permissão negada. Apenas ADMIN.{RESET}")
        pausar()
        return

    while True:
        limpar()
        cabecalho("GERENCIAR USUÁRIOS")

        usuarios = list_users(session.username)
        if usuarios:
            print(f"\n{CYAN}Usuários cadastrados:{RESET}")
            print(f"{DIM}{'Usuário':<15} {'Perfil':<12} {'Ativo':<8} {'Criado em'}{RESET}")
            print(f"{DIM}{'─' * 55}{RESET}")
            for u in usuarios:
                ativo = f"{GREEN}Sim{RESET}" if u["active"] else f"{RED}Não{RESET}"
                print(f"{u['username']:<15} {u['role']:<12} {ativo:<8} {u.get('created', 'N/A')[:10]}")
        else:
            print(f"\n{RED}Nenhum usuário encontrado.{RESET}")

        print(f"\n{CYAN}[1]{RESET} Criar usuário")
        print(f"{CYAN}[2]{RESET} Desativar usuário")
        print(f"{CYAN}[0]{RESET} Voltar")

        opcao = input(f"\n{WHITE}Escolha: {RESET}").strip()

        if opcao == "1":
            novo_user = input(f"{WHITE}Nome do usuário: {RESET}").strip()
            nova_senha = input(f"{WHITE}Senha (min 8 chars): {RESET}").strip()
            novo_perfil = input(f"{WHITE}Perfil (CONSULTA/OPERADOR/AUDITOR/ADMIN): {RESET}").strip().upper()
            ok, msg = create_user(novo_user, nova_senha, novo_perfil, session.username)
            print(f"\n{GREEN if ok else RED}{msg}{RESET}")
            pausar()
        elif opcao == "2":
            user_desativar = input(f"{WHITE}Usuário a desativar: {RESET}").strip()
            ok, msg = deactivate_user(user_desativar, session.username)
            print(f"\n{GREEN if ok else RED}{msg}{RESET}")
            pausar()
        elif opcao == "0":
            return


# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════

def main():
    while not session.is_valid():
        if not tela_login():
            limpar()
            print(f"\n{MAGENTA}Até mais! 👋{RESET}\n")
            sys.exit(0)

    while True:
        if not session.is_valid():
            print(f"\n{RED}Sessão expirada! Faça login novamente.{RESET}")
            pausar()
            if not tela_login():
                break
            continue

        menu()
        opcao = input(f"\n{CYAN}Escolha uma opção: {RESET}").strip()

        if opcao == "1":
            consulta_cep()
        elif opcao == "2":
            consulta_cnpj()
        elif opcao == "3":
            consulta_ip()
        elif opcao == "4":
            limpar()
            meu_ip()
        elif opcao == "5":
            consulta_pessoa()
        elif opcao == "8":
            logout(session)
            print(f"\n{MAGENTA}Logout realizado.{RESET}")
            pausar()
            while not session.is_valid():
                if not tela_login():
                    limpar()
                    print(f"\n{MAGENTA}Até mais! 👋{RESET}\n")
                    sys.exit(0)
        elif opcao == "0":
            logout(session)
            limpar()
            print(f"\n{MAGENTA}Até mais! 👋{RESET}\n")
            break
        else:
            print(f"\n{RED}Opção inválida.{RESET}")
            pausar()


if __name__ == "__main__":
    main()

