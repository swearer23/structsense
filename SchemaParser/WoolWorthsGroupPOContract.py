def parse_to_u8_schema(key_info):
  podetails = []
  pomain = {
    "ccusperson": {
      "value": key_info.get('contactName'),
      "name": "客户联系人"
    },
    'cSOCode': {
      "value": key_info.get('purchaseOrderNumber'),
      "name": "销售订单号"
    },
    'cSCCode': {
      "value": key_info.get('shipmentType'),
      "name": "发运方式"
    },
    'cexch_name': {
      "value": key_info.get('currency'),
      "name": "币种名称"
    },
    'cCusName': {
      "value": key_info.get('company_address'),
      "name": "客户名称"
    },
    'dPreDateBT': {
      "value": key_info.get('shipNoLaterThan'),
      "name": "预发货日期"
    },
  }
  for sku in key_info.get('SKU'):
    podetails.append({
      'iQuantity': {
        "value": sku.get('QTY'),
        "name": "数量"
      },
      'iUnitPrice': {
        "value": sku.get('price_per_unit'),
        "name": "原币无税单价"
      },
      'iMoney': {
        "value": sku.get('total_price'),
        "name": "原币无税金额"
      },
      'iCusBomID': {
        "value": sku.get('GTIN'),
        "name": "客户BOMID"
      },
    })
  return pomain, podetails, key_info