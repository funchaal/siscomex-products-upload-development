from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile

import requests
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates


@contextmanager
def pfx_to_pem(pfx_path, pfx_password):
    ''' Decrypts the .pfx file to be used with requests. '''
    pfx = Path(pfx_path).read_bytes()
    private_key, main_cert, add_certs = load_key_and_certificates(pfx, pfx_password.encode('utf-8'), None)

    with NamedTemporaryFile(suffix='.pem', delete=False) as t_pem:
        with open(t_pem.name, 'wb') as pem_file:
            pem_file.write(private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
            pem_file.write(main_cert.public_bytes(Encoding.PEM))
            for ca in add_certs:
                pem_file.write(ca.public_bytes(Encoding.PEM))
        yield t_pem.name

def autorizate(cert_path='', psw='', prod=False):
    # Autoriza a conexão com a API com o certificado digital.

    auth_url = 'https://val.portalunico.siscomex.gov.br/portal/api/autenticar'
    
    if prod:
        auth_url = 'https://portalunico.siscomex.gov.br/portal/api/autenticar'

    auth_headers = {
        "Role-Type": "IMPEXP"
    }

    set_token = ''
    csrf_token = ''

    with pfx_to_pem(cert_path, psw) as cert:
        response = requests.post(auth_url, cert=cert, headers=auth_headers)

        print("Autenticando...\n")

        print(response.headers)

        set_token = response.headers['set-token']
        csrf_token = response.headers['x-csrf-token']

        print('Autenticado!\n')

        return { 'set-token': set_token, 'csrf-token': csrf_token }