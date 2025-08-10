
from modules.utils import selectFile
from modules.autorization import autorizate

from openpyxl import Workbook
import os

import requests

def consultar_operadores(execution_folder, prod):
    set_token, csrf_token = None, None
    
    cert_path = selectFile(extension=".pfx")
    cert_psw = input('Digite a senha do certificado: ')

    raiz = input('Digite a raiz do CNPJ/CPF: ').strip().zfill(8)

    if not set_token:
        set_token, csrf_token = autorizate(cert_path, cert_psw, prod=prod).values()

    root_url = 'https://portalunico.siscomex.gov.br' if prod else 'https://val.portalunico.siscomex.gov.br'
    get_oe_url = f'{root_url}/catp/api/ext/operador-estrangeiro'

    headers = {
        "Content-Type": "application/json",
        "Authorization": set_token,
        "X-CSRF-Token": csrf_token
    }

    filters = {
        'cpfCnpjRaiz': raiz,
        'situacao': 0
    }

    try:
        print("Enviando requisição para obter operadores estrangeiros...")
        response = requests.get(get_oe_url, headers=headers, params=filters)

        if response.status_code != 200:
            print(f"Erro ao enviar requisição: {response.status_code}")
            print("Detalhes:", response.text)
            exit()

        print("Requisição enviada com sucesso!")
        results = response.json()

    except requests.exceptions.RequestException as e:
        print(f"Erro na conexão: {e}")
        exit()

    wb = Workbook()
    ws = wb.active
    ws.title = 'Operadores Estrangeiros'

    ws.append([
        'Código', 'Raiz', 'Nome', 'Situação',
        'Logradouro', 'Nome Cidade', 'Código País', 'Código Interno'
    ])

    for oe in results:
        ws.append([
            oe.get('codigo', ''),
            oe.get('cpfCnpjRaiz', ''),
            oe.get('nome', ''),
            oe.get('situacao', ''),
            oe.get('logradouro', ''),
            oe.get('nomeCidade', ''),
            oe.get('codigoPais', ''),
            oe.get('codigoInterno', '')
        ])

    file_path = os.path.join(execution_folder, 'oes.xlsx')
    wb.save(file_path)
    os.startfile(file_path)
    print(f"Arquivo Excel gerado com sucesso! Consulte o arquivo: {file_path}")