"""Crée .env avec deux clés d'API aléatoires (client et admin). Ne touche pas un .env déjà configuré."""
import secrets
from pathlib import Path

ENV = Path(__file__).resolve().parents[1] / ".env"

if ENV.exists() and "API_KEYS=" in ENV.read_text(encoding="utf-8") \
        and "remplacez" not in ENV.read_text(encoding="utf-8"):
    print(".env existe déjà avec des clés : rien à faire.")
    for ligne in ENV.read_text(encoding="utf-8").splitlines():
        if ligne.startswith("API_KEY="):
            print(f"Clé client (pour la page web) : {ligne.split('=', 1)[1]}")
else:
    client, admin = secrets.token_urlsafe(24), secrets.token_urlsafe(24)
    ENV.write_text(
        f"API_KEYS={client}:client,{admin}:admin\n"
        f"API_KEY={client}\n"
        "API_URL=http://127.0.0.1:8000\n"
        "CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500\n",
        encoding="utf-8",
    )
    print(".env créé avec 2 clés d'API.")
    print(f"Clé client (pour la page web) : {client}")
    print(f"Clé admin  (pour /v1/modele)  : {admin}")
