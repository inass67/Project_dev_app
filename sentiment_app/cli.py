"""Commande « sentiment » (TP6).

  sentiment --version
  sentiment predict "Livraison rapide, très satisfait"
  sentiment serve [--port 8000]
"""
import argparse
import sys

from sentiment_app import __version__


def _predict(texte: str) -> int:
    from sentiment_app.predict import classer

    try:
        verdict = classer(texte)
    except FileNotFoundError as erreur:
        print(f"erreur : {erreur}", file=sys.stderr)
        return 1
    except ValueError as erreur:
        print(f"erreur : {erreur}", file=sys.stderr)
        return 2
    # Le même seuil d'abstention que l'API : la commande et l'API donnent le même verdict
    print(f"{verdict['label']} {verdict['score']}")
    return 0


def _serve(hote: str, port: int) -> int:
    import uvicorn

    uvicorn.run("api.main:app", host=hote, port=port)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sentiment", description="Classe le sentiment d'un avis en français.")
    parser.add_argument("--version", action="version", version=f"sentiment-app {__version__}")
    commandes = parser.add_subparsers(dest="commande", required=True)
    p = commandes.add_parser("predict", help="classer un avis")
    p.add_argument("texte", nargs="+", help="l'avis à classer")
    s = commandes.add_parser("serve", help="lancer l'API sur http://127.0.0.1:8000")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    if args.commande == "predict":
        return _predict(" ".join(args.texte))
    return _serve(args.host, args.port)


if __name__ == "__main__":
    raise SystemExit(main())
