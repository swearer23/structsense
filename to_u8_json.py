from pprint import pprint
from parse_key_info import parse

def main():
  pdf_path = './docs/PurchaseOrder47648175.PDF'
  key_info = parse(pdf_path, eps=100)
  sub_orders = []
  ret = {
    "ccusperson": key_info.get('contactName'),
    'cSOCode': key_info.get('purchaseOrderNumber'),
    'cSCCode': key_info.get('shipmentType'),
    'cexch_name': key_info.get('currency'),
    'cCusName': key_info.get('company_address'),
    'dPreDateBT': key_info.get('shipNoLaterThan'),
    'subOrders': sub_orders,
  }
  for sku in key_info.get('SKU'):
    sub_orders.append({
      'iQuantity': sku.get('QTY'),
      'iUnitPrice': sku.get('price_per_unit'),
      'iMoney': sku.get('total_price'),
      'iCusBomID': sku.get('GTIN'),
    })
  return ret

if __name__ == '__main__':
  # pdf_path = './docs/PO1077867-0.PDF'
  # key_info = main(pdf_path, 'PrimarkPOContract', eps=30)
  u8_so_main = main()
  pprint(u8_so_main)