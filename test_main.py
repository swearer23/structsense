import os
import pytest
from to_u8_json import main as to_u8_json_main

def test_to_u8_json():
    for clsname in ['PrimarkPOContract', 'WoolWorthsGroupPOContract']:
        if clsname == 'PrimarkPOContract':
            eps = 30
        elif clsname == 'WoolWorthsGroupPOContract':
            eps = 100
        for file_name in os.listdir(f'./docs/{clsname}'):
            pdf_path = f'./docs/{clsname}/{file_name}'
            try:
                to_u8_json_main(clsname, pdf_path, eps=eps)
            except Exception as e:
                print('Error:', pdf_path)
                raise e

if __name__ == '__main__':
    pytest.main(['-s', './unittests/main.py'])
    test_to_u8_json()
    