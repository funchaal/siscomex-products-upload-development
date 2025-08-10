from modules.utils import excel_to_dict, post_payload, selectFile
from modules.autorization import autorizate

from modules.makeLinksPayload import makeLinksPayload
import os

import pandas as pd

def make_links(execution_folder, prod):
    set_token, csrf_token = None, None
    
    cert_path = selectFile(extension=".pfx")
    cert_psw = input('Digite a senha do certificado: ')

    df = selectFile()
    links = excel_to_dict(df)

    if not set_token:
        set_token, csrf_token = autorizate(cert_path, cert_psw, prod=prod).values()

    payload, errors = makeLinksPayload(links, set_token=set_token, csrf_token=csrf_token, prod=prod)

    # Salvar erros, se houver
    if errors:
        error_file = os.path.join(execution_folder, 'errors.xlsx')
        pd.DataFrame(errors).to_excel(error_file, index=False)
        os.startfile(error_file)
        print(f"Alguns erros ocorreram. Consulte o arquivo: {error_file}")

    if not payload:
        print("Nenhum dado para enviar.")
        exit()

    # Salvar payload para conferência
    data_file = os.path.join(execution_folder, 'payload.xlsx')
    pd.DataFrame(payload).to_excel(data_file, index=False)
    os.startfile(data_file)
    print(f"Dados prontos para envio. Consulte o arquivo: {data_file}")

    # Pergunta ao usuário se deseja enviar os dados
    post_confirmation = input('Deseja enviar os operadores estrangeiros? (s/n): ').strip().lower()
    if not ('s' in post_confirmation or 'y' in post_confirmation):
        print("Operação cancelada pelo usuário.")
        exit()

    url_path = '/catp/api/ext/fabricante'
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