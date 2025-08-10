from modules.makeFillSheet import makeFillSheet
from modules.utils import get_relation_json, selectFile
from modules.autorization import autorizate
import os

import pandas as pd

import requests

def consultar_produtos(execution_folder, prod):
    set_token, csrf_token = None, None

    cert_path = selectFile(extension=".pfx")
    cert_psw = input('Digite a senha do certificado: ')

    raiz = input('Digite a raiz do CNPJ/CPF: ').strip().zfill(8)

    if not set_token:
        set_token, csrf_token = autorizate(cert_path, cert_psw, prod=prod).values()

    root_url = 'https://portalunico.siscomex.gov.br' if prod else 'https://val.portalunico.siscomex.gov.br'
    get_products_url = f'{root_url}/catp/api/ext/produto'

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
        print("Enviando requisição para obter produtos...")
        response = requests.get(get_products_url, headers=headers, params=filters)

        if response.status_code != 200:
            print(f"Erro ao enviar requisição: {response.status_code}")
            print("Detalhes:", response.text)
            exit()

        print("Requisição enviada com sucesso!")
        results = response.json()

    except requests.exceptions.RequestException as e:
        print(f"Erro na conexão: {e}")
        exit()

    all_attr_codes = sorted(set(
        attr.get('atributo')
        for product in results
        for attr in product.get('atributos', [])
    ))

    registros = []

    for product in results:
        codigos_interno = product.get('codigosInterno')
        print(codigos_interno)
        base = {
            'Código': product.get('codigo', ''),
            'NCM': product.get('ncm', ''),
            'Raiz': product.get('cpfCnpjRaiz', ''),
            'Descrição': product.get('descricao', ''),
            'Denominação': product.get('denominacao', ''),
            # 'Código Interno': product.get('codigosInterno', [''])[0],
            'Código Interno': codigos_interno[0] if isinstance(codigos_interno, list) and codigos_interno else '', 
            'Modalidade': product.get('modalidade', ''),
            'Situação': product.get('situacao', ''),
            'Versão': product.get('versao', '')
        }

        attr_dict = {attr.get('atributo'): attr.get('valor') for attr in product.get('atributos', [])}
        for code in all_attr_codes:
            base[code] = attr_dict.get(code, '')
        registros.append(base)

    df_produtos = pd.DataFrame(registros)
    relation_json = get_relation_json(prod=prod)
    final_wb = makeFillSheet(df_produtos, relation_json)

    file_path = os.path.join(execution_folder, 'products.xlsx')
    final_wb.save(file_path)
    os.startfile(file_path)
    print(f"Arquivo Excel gerado com sucesso! Consulte o arquivo: {file_path}")