"""Authentification par clé d'API (en-tête X-API-Key) et autorisation par rôle."""
import os
import secrets
from collections.abc import Callable
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

Role = Literal["client", "admin"]
ROLES: tuple[str, ...] = ("client", "admin")
LONGUEUR_MIN = 16
EN_TETE = APIKeyHeader(name="X-API-Key", auto_error=False, description="Clé d'API")
NON_AUTHENTIFIE = {"WWW-Authenticate": "APIKey"}


def charger_cles(brut: str | None = None) -> dict[str, Role]:
    """Lit API_KEYS. Sans clé configurée, personne n'entre : on ferme par défaut."""
    brut = os.environ.get("API_KEYS", "") if brut is None else brut
    cles: dict[str, Role] = {}
    for entree in filter(None, (morceau.strip() for morceau in brut.split(","))):
        cle, _, role = entree.rpartition(":")
        if role not in ROLES:
            raise ValueError(f"rôle inconnu dans API_KEYS : {role!r} (attendu : client ou admin)")
        if len(cle) < LONGUEUR_MIN:
            # on ne recopie jamais la clé dans un message d'erreur : il finirait dans les journaux
            raise ValueError(f"clé trop courte dans API_KEYS ({len(cle)} caractères, minimum {LONGUEUR_MIN})")
        cles[cle] = role  # type: ignore[assignment]
    return cles


def identifier(cle: Annotated[str | None, Security(EN_TETE)]) -> Role:
    """Authentification : renvoie le rôle de l'appelant, ou lève une 401."""
    if not cle:
        raise HTTPException(401, "Clé d'API manquante : en-tête X-API-Key", headers=NON_AUTHENTIFIE)
    for connue, role in charger_cles().items():
        # compare_digest : temps constant, la clé ne se devine pas lettre par lettre
        if secrets.compare_digest(cle.encode(), connue.encode()):
            return role
    raise HTTPException(401, "Clé d'API invalide", headers=NON_AUTHENTIFIE)


def exiger(*autorises: Role) -> Callable[[Role], Role]:
    """Autorisation : fabrique une dépendance qui n'accepte que les rôles donnés."""

    def verifier(role: Annotated[Role, Depends(identifier)]) -> Role:
        if role not in autorises:
            raise HTTPException(403, f"Accès refusé au rôle « {role} »")
        return role

    return verifier
