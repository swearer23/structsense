def parse_to_u8_schema(key_info):
  podetails = []
  pomain = {
    "ccusperson": {
      "value": key_info.get('Buyer'),
      "name": "客户联系人"
    },
    'cSOCode': {
      "value": key_info.get('purchaseOrderNumber'),
      "name": "销售订单号"
    },
    'cSCCode': {
      "value": key_info.get('delivery_details')[0].get('Transport Mode'),
      "name": "发运方式"
    },
    'cexch_name': {
      "value": key_info.get('Currency'),
      "name": "币种名称"
    },
    'cCusName': {
      "value": 'Primark Limited',
      "name": "客户名称"
    },
    'dPreDateBT': {
      "value": key_info.get('delivery_details')[0].get('Handover Date'),
      "name": "预发货日期"
    },
  }

  skus = {}

  for delivery in key_info.get('delivery_details'):
    for order in delivery.get('delivery_orders'):
      for o in order.get('order_body'):
        pack_id = o.get('Pack Id')
        GTIN = [
          x.get('Pack GTIN')
          for x in key_info.get('package_info')
          if x.get('Pack Id') == pack_id
        ]
        GTIN = GTIN[0] if GTIN else ''
        if skus.get(GTIN):
          skus[GTIN]['qty'] += int(o.get('Units').replace(',', ''))
        else:
          skus[GTIN] = {
            'qty': int(o.get('Units').replace(',', '')),
            'price_per_unit': float(order.get('order_header')[0].get('Supplier Cost').replace('$', '')),
          }

  for skuid in skus.keys():
    sku = skus.get(skuid)
    total_price = round(sku.get('qty') * sku.get('price_per_unit'))
    podetails.append({
      'iQuantity': {
        "value": sku.get('qty'),
        "name": "数量"
      },
      'iUnitPrice': {
        "value": sku.get('price_per_unit'),
        "name": "原币无税单价"
      },
      'iMoney': {
        "value": total_price,
        "name": "原币无税金额"
      },
      'iCusBomID': {
        "value": skuid,
        "name": "客户BOMID"
      },
    })
  return pomain, podetails, key_info