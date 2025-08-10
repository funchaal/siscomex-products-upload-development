import pandas as pd


def makeProductsRetify(products, attributes_json):
    
    results = []

    errors = []

    seq = 0

    for product in products:

        seq += 1

        ncm = str(product['ncm']).replace('.', '')
        descricao = str(product['descricao'])
        denominacao = str(product['denominacao'])
        raiz = (str(product['raiz']).replace('.', ''))[:8]
        situacao = str(product['situacao']).upper()
        modalidade = str(product['modalidade']).upper()
        codigointerno = str(product['codigoInterno']).strip()
        codigo = str(product['codigo']).strip()

        attribute_array = product['atributos']

        results.append({
            'seq': seq, 
            'descricao': descricao, 
            'codigo': codigo, 
            'denominacao': denominacao, 
            'cpfCnpjRaiz': raiz, 
            'situacao': 'DESATIVADO', 
            'modalidade': 'IMPORTACAO', 
            'ncm': ncm, 
            # 'codigosInterno': [codigointerno], 
            'versao': '1'
            # 'atributos': []
        })

        ncm_dict = next((x for x in attributes_json['listaNcm'] if str(x['codigoNcm']).replace('.', '') == ncm), None)

        for attr_dict in ncm_dict['listaAtributos']:

            attr_code = str(attr_dict['codigo']).strip()

            attr_dtls_dict = next((x for x in attributes_json['detalhesAtributos'] if str(x['codigo']).strip() == attr_code), None)

            attr_name = str(attr_dtls_dict['nomeApresentacao']).strip().lower()
            attr_value = None

            for attr in attribute_array:
                if attr['code'] == attr_code or attr['name'] in attr_name:
                    attr_value = attr['value']
                    break
        
            # results[-1]['atributos'].append({
            #     'atributo': attr_code, 
            #     'valor': attr_value
            # })

            if not attr_value:

                errors.append({
                    'seq': seq, 
                    'atributo': attr_code, 
                    'nome': attr_name, 
                    'valor': attr_value, 
                    'erro': 'Não foi possível associar um valor.'
                })

            else:
                if attr_dtls_dict['atributoCondicionante']:
                    for attr_cond_dict in attr_dtls_dict['condicionados']:

                        logic = attr_cond_dict['condicao']['operador']
                        condition_value = attr_cond_dict['condicao']['valor']

                        if eval(f'not "{attr_value}" {logic} "{condition_value}"'):
                            continue

                        attr_cond_code = str(attr_cond_dict['atributo']['codigo']).strip()
                        attr_cond_name = str(attr_cond_dict['atributo']['nomeApresentacao']).strip().lower()

                        attr_cond_value = None

                        for attr in attribute_array:
                            if attr['code'] == attr_cond_code or attr['name'] in attr_cond_name:
                                attr_cond_value = attr['value']
                                break
                    
                        # results[-1]['atributos'].append({
                        #     'atributo': attr_cond_code, 
                        #     'valor': attr_cond_value
                        # })

                        if not attr_cond_value:

                            errors.append({
                                'seq': seq, 
                                'atributo': attr_cond_code, 
                                'nome': attr_cond_name, 
                                'valor': attr_cond_value, 
                                'erro': 'Não foi possível associar um valor.'
                            })

    return results, errors
