from Parser.base import BasePOContract
from pprint import pprint
from itertools import chain
import re
import pandas as pd

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
    pd = self.text_cluster.get('tables')[0]['pd']
    return pd.iloc[0, 6].replace('\n', ' ')
  
  def get_order_meta_info(self):
    pd = self.text_cluster.get('tables')[0]['pd']
    sub_pd = pd.iloc[1:6, :].copy().dropna(axis=1, how='all')
    ret = {}
    for pair in list(chain.from_iterable(sub_pd.values.tolist())):
      [k, v] = [x.strip() for x in pair.split(':')]
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
            [x for x in row if x != '']
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
      if table == start_table:
        # print(table.df)
        # print([x for x in table.df.columns.values.tolist() if not x.startswith('Col')])
        flag_start = True
      if not flag_start: continue
      # text = table.df.to_string(index=False, header=True)
      # print(111111111, 'Destination Number' in text, text)
      if 'Destination Number' in table.df.to_string(index=True, header=True):
        if 'Delivery Totals' in table.df.to_string(index=False, header=False):
          total_info = ([
            x for x in table.df.iloc[1, :].copy().values.tolist()
            if x is not None and x != '' and x != '0'
          ])
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

        columns = [
          x for x in table.df.columns.values.tolist()
          if x is not None and not x.startswith('Col') and x != ''
        ]
        rows = [
          x for x in table.df.iloc[0].copy().values.tolist()
          if x is not None and x != '' and x != '0'
        ]
        order_header = pd.DataFrame([rows], columns=columns)
        order_body = table.df[1:].copy()
        if not order_body.empty:
          columns = [x for x in order_body.iloc[0].values.tolist() if x is not None]
          rows = [
            [x for x in row if x is not None and x != '']
            for row in order_body.iloc[1:, :].copy().values.tolist() 
          ]
          order_body = pd.DataFrame(rows, columns=columns)
          ret.get('delivery_orders').append({
            "order_header": order_header.to_dict('records'),
            "order_body": order_body.to_dict('records')
          })
    return ret
  
  def get_delivery_detail(self):
    ret = []
    for idx, block in enumerate(self.blocks):
      text = block.get_text()
      if text.startswith('Delivery Number'):
        meta = {}
        for i in range(idx, idx + 3):
          for n in self.blocks[i].get_text().replace(':\n', ':').split('\n'):
            if ':' in n:
              k, v = [x for x in n.split(':')]
              meta[k] = v.strip()
        start_table = self.tables.get_first_table_after_rect(block)
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