from modules.utils import selectFile
from modules.autorization import autorizate

from openpyxl import Workbook

import os

import requests
import json
import io
import zipfile

def consultar_links(execution_folder, prod):
    set_token, csrf_token = None, None
    
    cert_path = selectFile(extension=".pfx")
    cert_psw = input('Digite a senha do certificado: ')

    raiz = input('Digite a raiz do CNPJ/CPF: ').strip().zfill(8)

    if not set_token:
        set_token, csrf_token = autorizate(cert_path, cert_psw, prod=prod).values()

    root_url = 'https://portalunico.siscomex.gov.br' if prod else 'https://val.portalunico.siscomex.gov.br'
    url = f'{root_url}/catp/api/ext/fabricante/exportar/{raiz}'

    headers = {
        "Authorization": set_token,
        "X-CSRF-Token": csrf_token
    }

    try:
        print("Enviando requisição para obter vínculos de fabricantes...")
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Erro ao enviar requisição: {response.status_code}")
            print("Detalhes:", response.text)
            exit()

        print("Requisição enviada com sucesso! Descompactando o ZIP...")

        # Abrir ZIP em memória
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        json_filename = next((f for f in zip_file.namelist() if f.endswith('.json')), None)
        if not json_filename:
            print("Erro: Arquivo JSON não encontrado no ZIP")
            exit()

        with zip_file.open(json_filename) as json_file:
            json_data = json.load(json_file)

    except requests.exceptions.RequestException as e:
        print(f"Erro na conexão: {e}")
        exit()
    except Exception as e:
        print(f"Erro inesperado: {e}")
        exit()

    # Criar planilha
    wb = Workbook()
    ws = wb.active
    ws.title = 'Vínculos'

    # Cabeçalhos
    ws.append([
        'seq', 'Código País', 'Raíz', 'Código Operador Estrangeiro',
        'Conhecido', 'Código Produto', 'Vincular'
    ])

    # Preencher dados
    for item in json_data:
        ws.append([
            item.get('seq', ''),
            item.get('codigoPais', ''),
            item.get('cpfCnpjRaiz', ''),
            item.get('codigoOperadorEstrangeiro', ''),
            item.get('conhecido', ''),
            item.get('codigoProduto', ''),
            item.get('vincular', '')
        ])

    # Salvar Excel
    file_path = os.path.join(execution_folder, 'vínculos.xlsx')
    wb.save(file_path)
    os.startfile(file_path)

    print(f"Arquivo Excel gerado com sucesso! Consulte o arquivo: {file_path}")