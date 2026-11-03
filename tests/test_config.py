from surveyor import config


def test_ceps_extras_sao_derivados_dos_ultimos_oito_digitos_dos_ras():
    assert config.CEP_EXTRA_INTEGRANTE_1 == "24100142"
    assert config.CEP_EXTRA_INTEGRANTE_2 == "24100467"


def test_velocidades_permitidas():
    assert config.VELOCIDADES_KMH == tuple(range(36, 81, 4))


def test_regras_basicas_configuradas():
    assert config.CEP_CAMPUS == "82821020"
    assert config.PRAZO_MAX_DIAS == 7
    assert config.FATOR_AUTONOMIA == 1.14
