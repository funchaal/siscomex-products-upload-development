import pandas as pd
from modules.utils import normalize_column_names

def makeOperatorsPayload(df):
    countries_df = pd.read_csv('./countries.csv', sep=';')

    possible_names = {
        'cpfCnpjRaiz': {
            'names': ['raiz', 'cnpj', 'cpf/cnpj raiz', 'cpf/cnpj', 'cpf'],
            'obrigatorio': True
        },
        'codigoInterno': {
            'names': ['codigo interno', 'cod interno', 'codigo operador', 'cod operador', 'codigo oe', 'cod oe', 'codigo op', 'cod op'],
            'obrigatorio': False
        },
        'cpfCnpjFabricante': {
            'names': ['fabricante', 'cpf/cnpj fabricante', 'cnpj fabricante', 'cpf fabricante'],
            'obrigatorio': False
        },
        'nome': {
            'names': ['nome', 'razao social', 'razao social do operador'],
            'obrigatorio': True
        },
        'logradouro': {
            'names': ['logradouro', 'endereco'],
            'obrigatorio': True
        },
        'vincular': {
            'names': ['vincular'],
            'obrigatorio': False
        },
        'conhecido': {
            'names': ['conhecido'],
            'obrigatorio': False
        },
        'nomeCidade': {
            'names': ['cidade', 'nome cidade', 'nome da cidade', 'municipio'],
            'obrigatorio': True
        },
        'cep': {
            'names': ['cep', 'codigo postal', 'codigo postal do operador'],
            'obrigatorio': False
        },
        'email': {
            'names': ['email', 'e-mail', 'email do operador', 'e-mail do operador'],
            'obrigatorio': False
        },
        'tin': {
            'names': ['tin'],
            'obrigatorio': False
        },
        'codigoPais': {
            'names': ['codigo pais', 'codigo do pais', 'cod do pais'],
            'obrigatorio': False
        },
        'pais': {
            'names': ['pais', 'nome pais', 'nome do pais', 'pais de origem', 'pais origem'],
            'obrigatorio': False
        },
        'versao': {
            'names': ['versao', 'versao (sistema)', 'versao operador', 'versao oe', 'versao op'],
            'obrigatorio': False
        },
        'codigoSubdivisaoPais': {
            'names': [
                'subdivisao pais', 'subdivisao do pais', 'codigo subdivisao pais',
                'codigo subdivisao do pais', 'subdivisao do pais (sistema)',
                'subdivisao pais (sistema)', 'codigo subdivisao pais (sistema)',
                'codigo subdivisao do pais (sistema)'
            ],
            'obrigatorio': False
        }
    }

    df = normalize_column_names(df, possible_names)

    payload, errors = []
    seq = 0

    for _, row in df.iterrows():
        seq += 1
        row_errors = []

        # Código do país a partir do nome, se não houver diretamente
        nome_pais = str(row.get('pais', '')).strip().lower()
        codigo_pais_input = str(row.get('codigoPais', '')).strip().upper()
        codigo_pais = (
            codigo_pais_input if codigo_pais_input else
            next(
                (
                    item['Code']
                    for _, item in countries_df.iterrows()
                    if nome_pais in str(item.get('nome', '')).strip().lower() or
                       str(item.get('nome', '')).strip().lower() in nome_pais
                ),
                None
            )
        )

        item = {'seq': seq}

        # Loop em todos os campos possíveis
        for campo, props in possible_names.items():
            valor = row.get(campo, '')

            # Aplicar regra de formatação específica
            if campo == 'cpfCnpjRaiz':
                valor_formatado = str(valor).replace('.', '').zfill(8)
            else:
                valor_formatado = str(valor).strip()

            # Substituir por código de país resolvido
            if campo == 'codigoPais':
                valor_formatado = codigo_pais or ''

            # Validação se for obrigatório
            if props.get('obrigatorio', False):
                if not valor_formatado:
                    row_errors.append(f"Campo obrigatório '{campo}' está em branco.")

            # Adiciona ao item se tiver valor
            if valor_formatado:
                # Campos booleanos
                if campo in ['vincular', 'conhecido']:
                    item[campo] = valor_formatado.lower().replace('ã', 'a') != 'nao' and valor_formatado != ''
                else:
                    item[campo] = valor_formatado

        # Acumula erros
        for err in row_errors:
            errors.append({
                'seq': seq,
                'codigo': str(row.get('codigoInterno', '')).strip(),
                'erro': err
            })

        payload.append(item)

    return payload, errors
