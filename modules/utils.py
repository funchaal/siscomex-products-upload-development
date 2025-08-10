import json
import requests
import zipfile
import io

import os
import pandas as pd

import re

import unicodedata

import math

import tkinter as tk
from tkinter import filedialog

from datetime import datetime

from typing import List, Dict, Any

def safe_json(obj):
    def fix_nan(o):
        if isinstance(o, float) and (math.isnan(o) or math.isinf(o)):
            return None
        elif isinstance(o, dict):
            return {k: fix_nan(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [fix_nan(i) for i in o]
        return o

    return fix_nan(obj)

def levenshtein(s1, s2):
    len_s1 = len(s1)
    len_s2 = len(s2)

    # Cria uma matriz (len_s1+1 x len_s2+1)
    dp = [[0 for _ in range(len_s2 + 1)] for _ in range(len_s1 + 1)]

    # Inicializa a primeira linha e coluna
    for i in range(len_s1 + 1):
        dp[i][0] = i
    for j in range(len_s2 + 1):
        dp[0][j] = j

    # Preenche a matriz
    for i in range(1, len_s1 + 1):
        for j in range(1, len_s2 + 1):
            if s1[i - 1] == s2[j - 1]:
                cost = 0
            else:
                cost = 1

            dp[i][j] = min(
                dp[i - 1][j] + 1,     # Deleção
                dp[i][j - 1] + 1,     # Inserção
                dp[i - 1][j - 1] + cost  # Substituição
            )

    return dp[len_s1][len_s2]

import re
import unicodedata

def normalize_column_names(df, possible_names):
    pn = possible_names.copy()

    # Função auxiliar para remover acentos e normalizar texto
    def normalize_text(text):
        text = text.lower()
        text = text.replace('ç', 'c')
        text = re.sub(r'[^\w\s]', '', text)
        text = unicodedata.normalize('NFKD', text)
        text = ''.join([c for c in text if not unicodedata.combining(c)])
        return text.strip()

    # Normaliza os nomes atuais das colunas do DataFrame
    normalized_columns = {col: normalize_text(col) for col in df.columns}

    # Novo dicionário para renomear colunas
    new_column_names = {}

    for original_col, normalized_col in normalized_columns.items():
        matched = False
        for final_name, config in pn.items():
            aliases = config['names']
            for alias in aliases:
                if alias == normalized_col:
                    new_column_names[original_col] = final_name
                    matched = True
                    break
            if matched:
                del pn[final_name]  # Evita duplicatas
                break

    df = df.rename(columns=new_column_names)

    return df


def get_relation_json(prod=False):
    file_path = f"attributes_relation_{'prod' if prod else 'val'}.json"

    # Verifica se o arquivo existe
    if os.path.exists(file_path):
        # Pega o timestamp de modificação
        mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        now = datetime.now()

        # Se o dia ou a hora forem diferentes, baixa novamente
        if True or mtime.date() == now.date() or mtime.hour == now.hour:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

    # Caso precise baixar novamente
    url = (
        'https://portalunico.siscomex.gov.br/cadatributos/api/atributo-ncm/download/json'
        if prod else
        'https://val.portalunico.siscomex.gov.br/cadatributos/api/atributo-ncm/download/json'
    )

    response = requests.get(url)

    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            nome_arquivo = z.namelist()[0]  # Nome do único arquivo no ZIP

            with z.open(nome_arquivo) as json_file:
                data = json.load(json_file)

        # Salva localmente para reutilização
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return data
    else:
        response.raise_for_status()

def excel_to_dict(df):
    results = []


    possible_names = {
        'codigo': {
            'names': ['codigo', 'cod'],
            'obrigatorio': False
        },
        'versao': {
            'names': ['versao', 'versao (sistema)', 'versao produto', 'versao prod'],
            'obrigatorio': False
        },
        'ncm': {
            'names': ['ncm'],
            'obrigatorio': True
        },
        'descricao': {
            'names': ['descricao'],
            'obrigatorio': True
        },
        'denominacao': {
            'names': ['denominacao'],
            'obrigatorio': True
        },
        'cpfCnpjRaiz': {
            'names': ['raiz', 'cnpj', 'cpf/cnpj raiz', 'cpf/cnpj', 'cpf', 'raiz cnpj', 'raiz cpf/cnpj'],
            'obrigatorio': True
        },
        'situacao': {
            'names': ['situacao'],
            'obrigatorio': False
        },
        'modalidade': {
            'names': ['modalidade'],
            'obrigatorio': False
        },
        'codigoInterno': {
            'names': ['codigo interno', 'cod interno', 'codigo produto', 'cod produto'],
            'obrigatorio': False
        }
    }

    df = normalize_column_names(df, possible_names)

    for _, row in df.iterrows():
        
        ncm = row.get('ncm', '')

        if not ncm: continue

        ncm = str(ncm).replace('.', '').strip()
        ncm = ncm.zfill(8)

        descricao = str(row.get('descricao', '')).strip()
        codigo = str(row.get('codigo', '')).strip()
        versao = str(row.get('versao', '')).strip()
        denominacao = str(row.get('denominacao', '')).strip()

        raiz = str(row.get('cpfCnpjRaiz', '')).replace('.', '').strip()[:8]
        raiz = raiz.zfill(8)

        situacao = str(row.get('situacao', 'ATIVADO')).strip().upper()
        modalidade = str(row.get('modalidade', 'IMPORTACAO')).strip().upper()
        codigointerno = str(row.get('codigoInterno')).strip()

        atributos = []
        
        for col in df.columns:
            if col not in ('codigo', 'versao', 'ncm', 'descricao', 'denominacao', 'codigoInterno', 'cpfCnpjRaiz', 'situacao', 'modalidade'):
                value = row[col]

                if '\n\n' in col:
                    col = col.split('\n\n')[0]
                match = re.match(r'^(ATT_\d+)\s*-\s*(.*)$', col)

                if match:
                    code = match.group(1).strip()
                    name = match.group(2).strip().lower()
                else:
                    match_alt = re.match(r'^(ATT_\d+)$', col.strip())
                    if match_alt:
                        code = match_alt.group(1).strip()
                        name = ''
                    else:
                        code = None
                        name = col
                atributos.append({'code': str(code).strip(), 'name': str(name).strip().lower(), 'value': value})

        results.append({
            'codigo': codigo, 
            'versao': versao, 
            'ncm': ncm, 
            'cpfCnpjRaiz': raiz, 
            'descricao': descricao, 
            'denominacao': denominacao, 
            'codigoInterno': codigointerno, 
            'modalidade': modalidade, 
            'situacao': situacao, 
            'atributos': atributos
        })
    
    return results

def post_payload(
    url_path: str, 
    headers: Dict[str, str], 
    payload: List[Dict[str, Any]], 
    chunk_size: int = 100, 
    prod: bool = True
) -> List[Dict[str, Any]]:

    root_url = 'https://portalunico.siscomex.gov.br/' if prod else 'https://val.portalunico.siscomex.gov.br/'
    url = root_url + url_path

    all_responses = []

    for idx in range(0, len(payload), chunk_size):
        chunk = payload[idx:idx + chunk_size]
        try:
            print(f"Enviando requisição para cadastrar produtos... (chunk {idx // chunk_size + 1})")
            print('chunk', chunk)

            response = requests.post(url, headers=headers, json=chunk)
            response.raise_for_status()  # primeiro verificar status!

            response_data = response.json()

            if isinstance(response_data, list):
                all_responses.extend(response_data)
            else:
                all_responses.append(response_data)

        except requests.exceptions.RequestException as e:
            print(f"Erro ao enviar requisição: {e}")

    return all_responses

def selectFile(extension=None):
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal

    # Define tipo de arquivo
    if extension:
        filetypes = [(f"Arquivos {extension.upper()}", f"*{extension}")]
    else:
        filetypes = [("Excel files", "*.xlsx;*.xls")]

    # Abre o seletor de arquivos
    file_path = filedialog.askopenfilename(
        title="Selecione um arquivo",
        filetypes=filetypes
    )

    if not file_path:
        print("Nenhum arquivo selecionado.")
        exit()

    # Se não foi passada extensão -> assume Excel e carrega
    if not extension:
        xls = pd.ExcelFile(file_path)
        sheets = xls.sheet_names

        # Se houver mais de uma planilha, pede para escolher
        if len(sheets) > 1:
            print(f"Planilhas disponíveis: {sheets}")
            sheet_name = input("Digite o nome da planilha que deseja abrir: ")
            while sheet_name not in sheets:
                sheet_name = input("Nome inválido! Digite um nome de planilha válido: ")
        else:
            sheet_name = sheets[0]

        df = pd.read_excel(file_path, sheet_name=sheet_name)
        print(f"Planilha '{sheet_name}' carregada com sucesso!")
        return df
    else:
        # Apenas retorna o caminho do arquivo
        return file_path