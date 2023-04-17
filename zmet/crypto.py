from hashlib import sha256
from base64 import (
	urlsafe_b64encode as b64_encode,
	urlsafe_b64decode as b64_decode,
)
from . import config
from Crypto.Cipher import AES



SECRET = sha256(("tokens?sk=" + config.app_secret_key).encode()).digest()


def gen_token(name: str, salt: str = ""):
	name_encoded = name.encode()
	if salt:
		name_encoded += b';' + salt.encode()

	# to avoid `=` symbol in b64 encoded token
	name_padded = name_encoded + ((- 16 - len(name_encoded)) % 3) * b"\x00"

	cipher = AES.new(SECRET, AES.MODE_EAX, nonce=16*b"\x00")
	ciphertext, tag = cipher.encrypt_and_digest(name_padded)
	return b64_encode(ciphertext + tag)


def decrypt_token(token):
	"""Returns (name, salt)"""
	token_bytes = b64_decode(token)
	ciphertext, tag = token_bytes[:-16], token_bytes[-16:]
	cipher = AES.new(SECRET, AES.MODE_EAX, nonce=16*b"\x00")
	name_padded = cipher.decrypt_and_verify(ciphertext, tag)
	name = name_padded.replace(b"\x00", b"").decode()
	if ';' in name:
		name, salt = name.split(';')
	else:
		salt = ""
	return (name, salt)
