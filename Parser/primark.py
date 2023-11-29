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
    def is_start(table):
      return table == start_table
    def is_end(table):
      all_text = ' '.join([
        ' '.join([
          y for y in x if y is not None
        ]) for x in table.df.values.tolist() if x is not None
      ])
      return 'Delivery Totals' in all_text
    ret = {
      "delivery_orders": [],
      "delivery_totals": {}
    }
    flag_start = False
    section_rows = []
    for table in self.tables:
      if is_start(table):
        flag_start = True
      
      if not flag_start: continue
      section_rows.append(table.df.columns.values.tolist())
      for i in range(table.df.shape[0]):
        section_rows.append(table.df.iloc[i, :].values.tolist())
      if is_end(table):
        flag_start = False
        break
    current_order = None
    idx = 0
    while idx < len(section_rows):
      row = section_rows[idx]
      row = [x for x in row if x is not None and x != '']
      if 'Delivery Totals' in ' '.join(row):
        ret['delivery_totals'] = {
          'total_unit': row[1],
          'total_packs': row[2],
          'total_value': row[3],
        }
      if 'Destination Number' in ' '.join(row) and 'Delivery Totals' not in ' '.join([
        x for x in
        section_rows[idx + 1]
        if x is not None and x != ''
      ]):
        if current_order:
          ret.get('delivery_orders').append(current_order)
          current_order = None
        columns = ['Destination Number', 'Destination', 'Units', 'Packs', 'Supplier Cost', 'Supplier Cost Value']
        order_header = pd.DataFrame([padding_number([
          x for x in section_rows[idx + 1]
          if x is not None and x != ''
        ])], columns=columns)
        current_order = {
          "order_header": order_header.to_dict('records'),
          "order_body": []
        }
      if 'Pack Id' in ' '.join(row):
        columns = [
          x if x != 'Unit' else 'Units'
          for x in row if x is not None and 'Col' not in x
        ]
        pack_rows = []
        idx +=1
        while 'Destination Number' not in ' '.join([
          x for x in
          section_rows[idx]
          if x is not None and x != ''
        ]):
          pack_row = section_rows[idx]
          clean_row = [
            x for x in pack_row
            if x is not None and x != '' and 'Col' not in x
          ]
          if len(clean_row) == 0:
            break
          pack_rows.append(clean_row)
          idx += 1
        order_body = pd.DataFrame(pack_rows, columns=columns)
        current_order['order_body'] = order_body.to_dict('records')
      idx += 1
    ret['delivery_orders'].append(current_order)
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