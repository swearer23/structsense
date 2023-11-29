import os
from pprint import pprint
import importlib
import pandas as pd
from parse_key_info import parse
from SchemaParser.WoolWorthsGroupPOContract import parse_to_u8_schema

def main(clsname='WoolWorthsGroupPOContract', pdf_path='./docs/PurchaseOrder47648175.PDF', eps=100):
  key_info = parse(pdf_path, eps=100, clsname=clsname)
  # pprint(key_info)
  module = importlib.import_module('SchemaParser.' + clsname)
  return module.parse_to_u8_schema(key_info)

def save_to_excel(pomain, podetails):
    with pd.ExcelWriter('./docs/PurchaseOrder47648175.xlsx') as writer:
        pomainCols = [v.get('name') for _, v in pomain.items()]
        pomainRow = [v.get('value') for _, v in pomain.items()]
        pd.DataFrame([pomainRow], columns=pomainCols).to_excel(writer, sheet_name='pomain', index=False)
        podetailsCols = [v.get('name') for _, v in podetails[0].items()]
        podetailsRows = [[v.get('value') for _, v in podetail.items()] for podetail in podetails]
        pd.DataFrame(podetailsRows, columns=podetailsCols).to_excel(writer, sheet_name='podetails', index=False)

def save_raw_to_excel(raw):
    sheet1_cols = [k for k, _ in raw.items() if k != 'SKU']
    sheet1_rows = [[v for k, v in raw.items() if k != 'SKU']]

    sheet2_cols = [k for k, _ in raw.get('SKU')[0].items()]
    sheet2_rows = [[v for _, v in sku.items()] for sku in raw.get('SKU')]
    with pd.ExcelWriter('./docs/PurchaseOrder47648175_Raw.xlsx') as writer:
      df_po_main = pd.DataFrame(sheet1_rows, columns=sheet1_cols)
      df_po_details = pd.DataFrame(sheet2_rows, columns=sheet2_cols)
      df_po_main.to_excel(writer, sheet_name='基本信息', index=False)
      df_po_details.to_excel(writer, sheet_name='SKU', index=False)

      # rawCols = [v.get('name') for _, v in raw.items()]
      # rawRow = [v.get('value') for _, v in raw.items()]
      # pd.DataFrame([rawRow], columns=rawCols).to_excel(writer, sheet_name='raw', index=False)

if __name__ == '__main__':
  # pdf_path = './docs/PO1077867-0.PDF'
  # key_info = main(pdf_path, 'PrimarkPOContract', eps=30)
  pomain, podetails, key_info = main(
    clsname='PrimarkPOContract',
    pdf_path = './docs/PO1077867-0.PDF',
    # pdf_path='./docs/PrimarkPOContract/Global-Mens Clothing-Mens Leisurewear-Mens Fashion Sweat Tops-1090236-1 (1).PDF',
    eps=30
  )
  # pprint(pomain)
  # pprint(podetails)
  # pprint(key_info)
  # save_to_excel(pomain, podetails)
  # save_raw_to_excel(key_info)
  # save to excel