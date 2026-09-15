# language: Python 3.10+, file: keygen.py
# Gera o par RSA. A privada é o que descriptografa — guarde-a.
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate(key_size: int = 2048):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    with open("private_key.pem", "wb") as f:
        f.write(private_pem)
    with open("public_key.pem", "wb") as f:
        f.write(public_pem)

    print("[+] private_key.pem  (nunca sobe pro GitHub)")
    print("[+] public_key.pem   (vai no binário / repo)")
    print()
    print("---- cole no README ou embuta no encrypter ----")
    print(public_pem.decode())

if __name__ == "__main__":
    generate()