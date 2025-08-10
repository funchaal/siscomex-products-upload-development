import pandas as pd

def makeProductsPayload(products, attributes_json):
    
    results = []

    errors = []

    seq = 0

    for product in products:

        seq += 1

        def clean(value):
            return '' if value is None or str(value).lower() == 'nan' else value

        codigo = clean(product.get('codigo'))
        versao = clean(product.get('versao'))
        ncm = clean(product.get('ncm'))
        descricao = clean(product.get('descricao'))
        denominacao = clean(product.get('denominacao'))
        raiz = clean(product.get('cpfCnpjRaiz'))
        situacao = clean(product.get('situacao', 'ATIVADO'))
        modalidade = clean(product.get('modalidade', 'IMPORTACAO'))
        codigointerno = clean(product.get('codigoInterno'))
        attribute_array = product.get('atributos', [])


        product_json = {'seq': seq}

        # Só adiciona se existir no product
        if codigo: product_json['codigo'] = codigo
        if descricao: product_json['descricao'] = descricao
        if denominacao: product_json['denominacao'] = denominacao
        if raiz: product_json['cpfCnpjRaiz'] = raiz
        if situacao: product_json['situacao'] = situacao
        if modalidade: product_json['modalidade'] = modalidade
        if ncm: product_json['ncm'] = ncm
        if versao: product_json['versao'] = versao
        if codigointerno: product_json['codigosInterno'] = [codigointerno]
        

        product_json['atributos'] = []
        product_json['atributosCompostos'] = []
        product_json['atributosMultivalorados'] = []

        results.append(product_json)

        attribute_array = product['atributos']

        def proccess_row(atribute_brute, cond_attr=False, obrigatorio=True, base_attribute=None, sub_attr=False, multivalue_attr=False):

            atribute = None

            if cond_attr:
                atribute = atribute_brute['atributo']

                def get_logic_string(logic_string, condicao):
                    composicao = condicao.get('composicao', None)
                    operador = condicao['operador']
                    valor = condicao['valor']

                    logic_string = f'"{base_attribute['valor']}" {operador} "{valor}"'
                    if composicao:
                        logic_string = f'({logic_string}) {str(composicao).replace('||', 'or')} '
                        get_logic_string(logic_string, condicao['condicao'])
                    else:
                        return logic_string
                    
                logic_string = get_logic_string('', atribute_brute['condicao'])

                if eval(f'not {logic_string}'):
                    return

            else:
                atribute = atribute_brute
            
            attr_code = atribute['codigo']
            attr_name = atribute['nomeApresentacao']
            attr_value = None

            # Verifica se tem subatributos
            if len(atribute['listaSubatributos']) > 0:

                results[-1]['atributosCompostos'].append({
                    'atributo': attr_code, 
                    'valores': []
                })

                for sub_attr in atribute['listaSubatributos']:
                    proccess_row(sub_attr, obrigatorio=sub_attr['obrigatorio'], sub_attr=True)
                
                return

            # Pega o valor do atributo
            for attr in attribute_array:
                if attr['code'] == attr_code or attr['name'] == str(attr_name).lower():
                    attr_value = str(attr['value']).strip()
                    break

            if attr_value == 'nan' or pd.isna(attr_value):
                attr_value = ''
            
            if not attr_value:
                if obrigatorio:
                    errors.append({
                        'seq': seq, 
                        'ncm': ncm,
                        'atributo': attr_code, 
                        'nome': attr_name + (' (Condicional)' if cond_attr else '') + (' (SubAtributo)' if sub_attr else ''), 
                        'valor': attr['value'], 
                        'erro': 'Não foi possível converter o valor para inteiro.'
                    })
                return
            
            if attr_code == 'ATT_11820':
                pass

            if atribute.get('formaPreenchimento') == 'LISTA_ESTATICA':
                for item in atribute.get('dominio', []):
                    if int(float(attr_value)) == int(float(item.get('codigo'))):
                        attr_value = item.get('codigo')
            
            if atribute.get('formaPreenchimento') == 'NUMERO_INTEIRO':
                try:
                    attr_value = str(int(float(attr_value)))
                except:
                    errors.append({
                        'seq': seq, 
                        'ncm': ncm,
                        'atributo': attr_code, 
                        'nome': attr_name + (' (Condicional)' if cond_attr else '') + (' (SubAtributo)' if sub_attr else ''), 
                        'valor': attr['value'], 
                        'erro': 'Não foi possível converter o valor para inteiro.'
                    })
                
            if attr_value.lower() == 'sim':
                attr_value = 'true'
            elif attr_value.lower().replace('ã', 'a') == 'nao':
                attr_value = 'false'
                
            if sub_attr:
                results[-1]['atributosCompostos'][-1]['valores'].append({
                    'atributo': attr_code, 
                    'valor': attr_value
                })
            else:
                # Acrescenta o atributo ao payload
                if multivalue_attr:
                    attr_values = attr_value.split(',')
                    attr_values = [v.strip() for v in attr_values]

                    results[-1]['atributosMultivalorados'].append({
                        'atributo': attr_code, 
                        'valores': attr_values
                    })
                else:
                    results[-1]['atributos'].append({
                            'atributo': attr_code, 
                            'valor': attr_value
                        })
            
            if atribute['atributoCondicionante']:
                for atribute_cond in atribute['condicionados']:
                    proccess_row(atribute_cond, cond_attr=True, obrigatorio=atribute_cond['atributo']['obrigatorio'], sub_attr=sub_attr, multivalue_attr=atribute_cond['multivalorado'], base_attribute={ 'atributo': attr_code, 'valor': attr_value })
            


        ncm_dict = next((x for x in attributes_json['listaNcm'] if str(x['codigoNcm']).replace('.', '') == ncm), None)

        for attr in ncm_dict['listaAtributos']:

            # if attr['codigo'] == 'ATT_11920':
            #     continue

            attr_dtls = next((d for d in attributes_json['detalhesAtributos'] if d['codigo'] == attr['codigo']), None)

            proccess_row(attr_dtls, obrigatorio=attr['obrigatorio'], multivalue_attr=attr['multivalorado'])

    return results, errors