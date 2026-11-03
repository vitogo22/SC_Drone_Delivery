"""Ponto de entrada do pacote: python -m surveyor."""
import argparse


def criar_parser() -> argparse.ArgumentParser:
    """Cria o parser da linha de comando."""
    parser = argparse.ArgumentParser(
        prog="surveyor",
        description="UNIBRASIL Surveyor — planejamento de rota de drone.",
    )
    parser.add_argument("--coordenadas", help="Caminho do CSV de coordenadas.")
    parser.add_argument("--extras", help="Caminho do CSV das coordenadas extras.")
    parser.add_argument("--saida", help="Caminho do CSV do plano de voo.")
    parser.add_argument("--semente", type=int, help="Semente para reprodutibilidade.")
    return parser


def main() -> None:
    """Executa a interface de linha de comando."""
    criar_parser().parse_args()


if __name__ == "__main__":
    main()
