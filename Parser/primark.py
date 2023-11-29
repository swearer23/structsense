from Parser.base import BasePOContract
from pprint import pprint
from itertools import chain
import re
import pandas as pd
from Parser.utils import padding_number

class PrimarkPOContract(BasePOContract):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def get_company_address(self):
    addrs = self.text_cluster.get('blocks_text')[4:8]
    return [" ".join(x).replace('\n', ' ') for x in addrs]
  
  def get_purchase_order_number(self):
    return self.flat_blocks_text[3].split(':')[1].strip()
  
  def get_supplier_info(self):
    pd = self.text_cluster.get('tables')[0]['pd']
    return pd.iloc[0, 0].replace('\n', ' ')
  
  def get_factory_info(self):
    line_one = self.tables[0].df.iloc[0, :].values.tolist()
    line_one = [x for x in line_one if x is not None and x != '']
    return line_one[1].split('\n')[1]
  
  def get_order_meta_info(self):
    pd = self.text_cluster.get('tables')[0]['pd']
    sub_pd = pd.iloc[1:, :].copy().dropna(axis=1, how='all')
    ret = {}
    for pair in list(chain.from_iterable(sub_pd.values.tolist())):
      if pair is None or ':' not in pair:
        continue
      [k, v] = [x.strip() for x in pair.split(':')]
      if k.startswith('Changes from prior'):
        break
      ret[k] = v
    return ret
  
  def get_delivery_summary(self):
    for i, line in enumerate(self.flat_blocks_text):
      if 'DELIVERY/DESTINATION SUMMARY' in line:
        start = i + 1
      if 'HANDOVER DATE' in line:
        end = i
        break
    ds = self.flat_blocks_text[start:end]
    ds = [x.strip() for x in '\n'.join(ds).replace('\n\n', '\n').split('\n') if len(x.strip()) > 0]
    ret = {}
    for line in ds:
      [k, v] = [x.strip() for x in line.split(':')]
      ret[k] = v
    return ret
  
  def get_delivery_tables(self):
    pattern = r'HANDOVER DATE: (\d{8}).*?DELIVERY: (\d+)'
    dtables = []
    for raw_table in self.text_cluster.get('tables'):
      table = raw_table['pd']
      meta = table.columns[0]
      if 'DELIVERY' in meta:
        matches = re.search(pattern, meta)
        if matches:
          # table.columns = table.iloc[0].values
          table = table.dropna(axis=1, how='all')
          cols = [x.replace('\n', ' ') for x in table.iloc[0].values if x is not None]
          rows = [
            [x for x in row if x != '' and x is not None]
            for row in table.iloc[1:, :].copy().values.tolist() 
          ]
          total_unit = rows[-1][-2]
          total_packs = rows[-1][-1]
          table = pd.DataFrame(rows[:-1], columns=cols)
          dtables.append({
            "delivery_number": matches.group(2),
            "table": table.to_dict('records'),
            "handover_date": matches.group(1),
            "total_unit": total_unit,
            "total_packs": total_packs
          })
    return dtables
  
  def get_package_info(self):
    package_info = []
    for block in self.blocks:
      text = block.get_text()
      if text.startswith('Pack Id:'):
        pack_basic_info = {}
        for n in text.split('\n'):
          if ':' in n:
            k, v = [x for x in n.split(':')]
            pack_basic_info[k] = v.strip()
        table = self.tables.get_first_table_after_rect(block)
        if table:
          package_info.append({
            **pack_basic_info,
            "table": table.df.to_dict('records')
          })
    return package_info
  
  def get_delivery_detail_tables(self, start_table):
    ret = {
      "delivery_orders": [],
      "delivery_totals": {}
    }
    flag_start = False
    for table in self.tables:
      print(table)
      if table == start_table:
        # print([x for x in table.df.columns.values.tolist() if not x.startswith('Col')])
        flag_start = True
      if not flag_start: continue
      # text = table.df.to_string(index=False, header=True)
      # print(111111111, 'Destination Number' in text, text)
      if 'Destination Number' in table.df.columns.values.tolist(): # to_string(index=True, header=True):
        print(table)
        for i in range(table.df.shape[0]):
          if 'Delivery Totals' in table.df.iloc[i, :].values.tolist():
            total_info = [
              x for x in table.df.iloc[i, :].copy().values.tolist()
              if x is not None and x != '' # and x != '0'
            ]
            # print(table.df.iloc[i, :].values.tolist())
            # print(total_info)
            ret['delivery_totals'] = {
              'total_unit': total_info[1],
              'total_packs': total_info[2],
              'total_value': total_info[3],
            }
            flag_start = False
            break
        
        if 'Destination Number' not in ' '.join(table.df.columns.values.tolist()):
          for i, row in enumerate(table.df.values.tolist()):
            if 'Destination Number' in row:
              table.df.columns = table.df.iloc[i, :].copy().values.tolist()
              table.df = table.df.drop(i)
              break

        # columns = [
        #   x for x in table.df.columns.values.tolist()
        #   if x is not None and not x.startswith('Col') and x != ''
        # ]
        columns = ['Destination Number', 'Destination', 'Units', 'Packs', 'Supplier Cost', 'Supplier Cost Value']
        rows = [
          x for x in table.df.iloc[0].copy().values.tolist()
          if x is not None and x != '' # and x != '0' # and 'Delivery Totals' not in x
        ]
        # print(table)
        # print(columns, 11111111111)
        # print(padding_number(rows), 11111111)
        # print(rows)
        # print(table.df.iloc[0].copy().values.tolist())

        order_header = pd.DataFrame([padding_number(rows)], columns=columns)
        order_body = table.df[1:].copy()
        if not order_body.empty:
          idx = 0
          columns = None
          while idx < order_body.shape[0]:
            print(order_body.iloc[idx, :].values.tolist(), 22222222222222)
            if 'Pack Id' in ' '.join([x for x in order_body.iloc[idx, :].values.tolist() if x is not None]):
              columns = [
                x if x != 'Unit' else 'Units'
                for x in order_body.iloc[idx].values.tolist() if x is not None
              ]
              break
            idx += 1
          if columns:
            # print(columns)
            rows = [
              [x for x in row if x is not None and x != '']
              for row in order_body.iloc[1:, :].copy().values.tolist()
              if 'Delivery Totals' not in row and 'Destination Number' not in row
            ]
            print('============')
            print(order_header)
            print(order_body)
            print(columns)
            print(rows)
            print('============')
            order_body = pd.DataFrame(rows, columns=columns)
            ret.get('delivery_orders').append({
              "order_header": order_header.to_dict('records'),
              "order_body": order_body.to_dict('records')
            })
    return ret
  
  def get_delivery_detail(self):
    split_keywords = [
      'Delivery Number',
      'Factory',
      'Transport Mode',
      'Handover Date',
      'COM',
      'Tickets',
      'H/F',
      'Incoterms',
      'Exit Port',
      'Confirmed'
    ]
    regex_pattern = '(' + '|'.join(re.escape(kw) for kw in split_keywords) + ')'
    ret = []
    for idx, block in enumerate(self.blocks):
      text = block.get_text()
      deli_info_str = ''
      deli_info_idx = idx
      if text.startswith('Delivery Number'):
        start_table = self.tables.get_first_table_after_rect(block)
        meta = {}

        while self.blocks[deli_info_idx].get_y_1() < start_table.rect[1]:
          deli_info_str += self.blocks[deli_info_idx].get_text()
          deli_info_idx += 1

        deli_info_str = deli_info_str.replace(':\n', ':').replace('\n', '')
        splitted_string = [x for x in re.split(regex_pattern, deli_info_str) if x != '']
        for j in range(0, len(splitted_string), 2):
          k, v = splitted_string[j], splitted_string[j + 1]
          meta[k] = v.split(':')[1].strip()
        delivery_tables = self.get_delivery_detail_tables(start_table)
        ret.append({
          **meta,
          **delivery_tables
        })

    return ret
  
  def parse(self, *args, **kwargs):
    delivery_tables = self.get_delivery_tables()
    order_meta_info = self.get_order_meta_info()
    delivery_summary = self.get_delivery_summary()
    delivery_details = self.get_delivery_detail()
    self.template = {
      **order_meta_info,
      **delivery_summary,
      "delivery_details": delivery_details,
      "delivery_tables": delivery_tables,
      "company_address": self.get_company_address(),
      "package_info": self.get_package_info(),
      "purchaseOrderNumber": self.get_purchase_order_number(),
      "vendor": self.get_supplier_info(),
      "factory": self.get_factory_info(),
    }
    return self.template