from modules.utils import post_payload, selectFile
from modules.autorization import autorizate

from modules.makeOperatorsPayload import makeOperatorsPayload
import os

import pandas as pd

def make_operators(execution_folder, prod):
    set_token, csrf_token = None, None
    
    cert_path = selectFile(extension=".pfx")
    cert_psw = input('Digite a senha do certificado: ')

    df = selectFile()

    payload, errors = makeOperatorsPayload(df)

    # Salvando erros, se houver
    if errors:
        error_file = os.path.join(execution_folder, 'errors.xlsx')
        pd.DataFrame(errors).to_excel(error_file, index=False)
        os.startfile(error_file)
        print(f"Alguns erros ocorreram. Consulte o arquivo: {error_file}")

    if payload:
        data_file = os.path.join(execution_folder, 'payload.xlsx')
        pd.DataFrame(payload).to_excel(data_file, index=False)
        os.startfile(data_file)
        print(f"Dados prontos para envio. Consulte o arquivo: {data_file}")
    else:
        print("Nenhum dado para enviar.")
        exit()

    # Pergunta ao usuário se deseja enviar os dados
    post_confirmation = input('Deseja enviar os operadores estrangeiros? (s/n): ').strip().lower()

    if not 's' in post_confirmation and not 'y' in post_confirmation:
        print("Operação cancelada pelo usuário.")
        exit()

    # Enviando os dados, se houver
    if not set_token:
        set_token, csrf_token = autorizate(cert_path, cert_psw, prod=prod).values()

    url_path = '/catp/api/ext/operador-estrangeiro'

    headers = {
        "Content-Type": "application/json",
        "Authorization": set_token,
        "X-CSRF-Token": csrf_token,
    }

    response = post_payload(url_path=url_path, headers=headers, payload=payload, chunk_size=100, prod=prod)
    if response:
        print("Requisição enviada com sucesso!")
        response_file = os.path.join(execution_folder, 'response.xlsx')
        pd.DataFrame(response).to_excel(response_file, index=False)
        os.startfile(response_file)
    else:
        print("Nenhuma resposta recebida ou erro ao enviar a requisição.")