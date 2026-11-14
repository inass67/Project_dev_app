"""sentiment_app : classer le sentiment d'un avis en français (TP6)."""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("sentiment-app")  # une seule source de vérité : pyproject.toml
except PackageNotFoundError:  # dépôt utilisé sans pip install -e .
    __version__ = "0.0.0"

__all__ = ["__version__"]
