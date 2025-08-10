import os
from modules.makeFillSheet import makeFillSheet
from modules.utils import get_relation_json, selectFile

def make_sheet(execution_folder, prod):
    df = selectFile()

    relation_json = get_relation_json(prod=prod)
    wb = makeFillSheet(df, relation_json, execution_folder)

    output_path = os.path.join(execution_folder, "fill.xlsx")

    wb.save(output_path)
    print(f"Arquivo salvo em: {output_path}")
