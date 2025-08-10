from modules.operations.consultar_produtos import consultar_produtos
from modules.operations.consultar_operadores import consultar_operadores
from modules.operations.consultar_links import consultar_links
from modules.operations.make_sheet import make_sheet
from modules.operations.make_products import make_products
from modules.operations.make_operators import make_operators
from modules.operations.make_links import make_links

import datetime
import os

PROD = False

OUTPUT_PATH = 'outputs'

execution_folder = os.path.join(OUTPUT_PATH, f'execution_{datetime.datetime.now().strftime("%d%m%Y_%H%M")}')
os.makedirs(execution_folder, exist_ok=True)

print(f"Pasta de execução criada: {execution_folder}")

if __name__ == "__main__":
    operation = 'cl'
    if operation == 'cp':
        consultar_produtos(execution_folder, prod=PROD)

    elif operation == 'co':
        consultar_operadores(execution_folder, prod=PROD)

    elif operation == 'cl':
        consultar_links(execution_folder, prod=PROD)
    
    if operation == 'ms':
        make_sheet(execution_folder, prod=PROD)

    if  operation == 'mp':
        make_products(execution_folder, prod=PROD)

    if operation == 'mo':
        make_operators(execution_folder, prod=PROD)

    if operation == 'ml':
        make_links(execution_folder, prod=PROD)