#Desafio Ransomware 

Objetivo: Implementa criptografia híbrida AES-256-GCM + RSA-2048,o mesmo modelo usado por famílias reais de ransomware (LockBit, REvil,
Conti), em escala didática e com modo de simulação.

## Arquitetura

```
encrypter.py  →  por arquivo:
                  1. gera chave AES-256 aleatória
                  2. gera nonce de 12 B
                  3. cifra com AES-256-GCM (autenticado)
                  4. envolve a chave AES com RSA-2048-OAEP
                  5. monta [nonce | wrapped_key | ciphertext]
                  6. apaga o original
```

### Por que híbrido?

AES é rápido mas exige chave compartilhada. RSA é lento e só cifra blocos pequenos. O padrão da indústria é **usar AES para o conteúdo
e RSA para proteger a chave do AES**. 

Assim:
- o binário carrega só a **pública** — quem o analisa não decifra nada
- o atacante guarda só a **privada** — uma única chave destrava N arquivos
- cada arquivo tem chave e nonce próprios — vazar um não compromete os outros

## Uso

```bash
pip install cryptography

# 1. gera o par de chaves
python keygen.py

# 2. coloque arquivos .txt de teste em sandbox/
mkdir sandbox && echo "segredo" > sandbox/teste.txt

# 3. com DRY_RUN=True em config.py — só simula
python encrypter.py

# 4. com DRY_RUN=False — cifra de verdade
python decrypter.py
```

## Estrutura dos arquivos cifrados

```
+--------+-----------------+----------------------+
| nonce  | wrapped_key     | ciphertext + tag     |
| 12 B   | 256 B (RSA-2048)| variável + 16 B      |
+--------+-----------------+----------------------+
```

## Aviso

Código com fins didáticos. A `private_key.pem` nunca deve ser comitada — adicione ao `.gitignore`.
