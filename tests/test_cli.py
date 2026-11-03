from surveyor.__main__ import criar_parser


def test_parser_tem_opcoes_previstas():
    parser = criar_parser()
    opcoes = {acao.dest for acao in parser._actions}
    assert {"coordenadas", "extras", "saida", "semente"} <= opcoes
