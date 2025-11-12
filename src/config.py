###Tasy

tasy_tratamento_columns = [
    "historia_da_doenca_atual",
    "evolucoes_queixas",
    "impressoes_medicas",
]

### REDCAP

src_drug_cols_dict = {
    "inducao": "Quais medicamentos foram usados \u200b\u200bpara terapia de inducao?",
    "consolidacao": "Quais medicamentos foram usados \u200b\u200bpara terapia de consolidacao?",
    "manutencao": "Quais medicamentos foram usados \u200b\u200bpara terapia de manutencao?",
}

final_drug_cols_dict = {
    "inducao": "inducao_medicamentos",
    "consolidacao": "consolidacao_medicamentos",
    "manutencao": "manutencao_medicamentos",
}

rename_columns_dict = {
    "Quando iniciou a terapia de inducao?": "inducao_start",
    "Quando terminou a terapia de inducao?": "inducao_end",
    "Quando a terapia de consolidacao comecou?": "consolidacao_start",
    "Quando terminou a terapia de consolidacao?": "consolidacao_end",
    "Quando comecou a terapia de manutencao?": "manutencao_start",
    "Quando terminou a terapia de manutencao?": "manutencao_end",
    "Data do inicio da radioterapia": "radio_start",
    "Data termino do tratamento da Radioterapia": "radio_end",
    "Data do transplante:": "transplant_dt",
    "Tipo de transplante:": "transplant_type",
}

label_cols = [
    "inducao_start",
    "inducao_end",
    final_drug_cols_dict["inducao"],
    "consolidacao_start",
    "consolidacao_end",
    final_drug_cols_dict["consolidacao"],
    "manutencao_start",
    "manutencao_end",
    final_drug_cols_dict["manutencao"],
    "radio_start",
    "radio_end",
    "transplant_dt",
    "transplant_type",
]
