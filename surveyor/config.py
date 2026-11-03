"""Constantes e decisões centralizadas do UNIBRASIL Surveyor."""

# Identificação da equipe
RA_INTEGRANTE_1 = "2024100142"
RA_INTEGRANTE_2 = "2024100467"
CEP_EXTRA_INTEGRANTE_1 = RA_INTEGRANTE_1[-8:]
CEP_EXTRA_INTEGRANTE_2 = RA_INTEGRANTE_2[-8:]

# Dados e percurso
CEP_CAMPUS = "82821020"
TOTAL_LINHAS_BASE = 374
TOTAL_PONTOS_CONSOLIDADOS = 376
TOTAL_PONTOS_A_VISITAR = 375
TOTAL_TRECHOS = 376

# Regras fixas do enunciado
VELOCIDADES_KMH = tuple(range(36, 81, 4))
HORA_INICIO = "06:00:00"
FIM_EXPEDIENTE = "17:00:00"  # D8: padrão para evitar taxa adicional
TETO_EXPEDIENTE = "19:00:00"
PRAZO_MAX_DIAS = 7
TEMPO_PARADA_SEM_POUSO_S = 60
TEMPO_PARADA_COM_POUSO_S = 172
TAXA_POUSO_REAIS = 80.0
TAXA_ADICIONAL_POUSO_APOS_17H_REAIS = 80.0

# D2 — fator aplicado à autonomia
FATOR_AUTONOMIA = 1.14

# D3 — função de custo única
VALOR_HORA = 80.0

# D4 — bateria consumida nas paradas à taxa de referência
RESERVA_BATERIA = 0.01

# D6 — modelo de vento
MODELO_VENTO = "exemplo_pdf"

# D1 — regras condicionais aplicadas à dupla até resposta do professor
APLICAR_REGRAS_CONDICIONAIS_RA_INICIADO_POR_2 = True

# D5 — pouso final no campus
POUSO_FINAL_CONTA_COMO_POUSO = True

# D7 — relógio: próxima saída na hora final ou depois do pouso
PROXIMA_SAIDA_APOS_HORA_FINAL = True

# D8 — limite operacional adotado para evitar a taxa adicional
USAR_FIM_EXPEDIENTE_COMO_LIMITE_OPERACIONAL = True
