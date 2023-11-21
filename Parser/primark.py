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
      text = block.get_text()[0]
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
  
  def get_delivery_detail(self):
    print(self.tables)
    pass
  
  def get_company_contact_info(self):
    company_contact = self.text_cluster.get('cluster').get(1)
    for i, str in enumerate(company_contact):
      if str.startswith('Phone'):
        company_phone = company_contact[i+1]
      if str.startswith('Fax'):
        company_fax = company_contact[i+1]
    return company_phone, company_fax
    
  def get_contact_info(self):
    contact_info = self.text_cluster.get('cluster').get(6)
    contact_name = contact_info[3]
    contact_phone = contact_info[4]
    contact_email = contact_info[5]
    return contact_name, contact_phone, contact_email
  
  def get_purchase_order_info(self):
    purchase_order_info = self.text_cluster.get('cluster').get(2)
    purchase_order_number = purchase_order_info[0].split(':')[-1].strip()
    ship_no_later_than = purchase_order_info[1].split(':')[-1].strip()
    port_arrival_date = purchase_order_info[2].split(':')[-1].strip()
    port_of_loading = purchase_order_info[3].split(':')[-1].strip()
    port_of_destination = purchase_order_info[4].split(':')[-1].strip()
    return purchase_order_number, ship_no_later_than, port_arrival_date, port_of_loading, port_of_destination
  
  
  
  def get_destination_info(self):
    destination_info = self.text_cluster.get('cluster').get(4)
    return " ".join(destination_info)
  
  def get_vendor_info(self):
    vendor_info = self.text_cluster.get('cluster').get(5)
    return " ".join(vendor_info).split(':')[1].strip()
  
  def get_total_value(self):
    [total_value] = [x for x in self.flat_blocks_text if 'Total Value' in x]
    return total_value.split(':')[1].strip()
  
  def get_sku_info(self):
    sku_pd = self.text_cluster.get('tables')[1].to_pandas()
    sku_pd.columns = sku_pd.iloc[0].values
    sku_pd = sku_pd.drop(0)
    return (sku_pd.to_dict('records'))
  
  def parse(self, *args, **kwargs):
    # company_phone, company_fax = self.get_company_contact_info()
    # contact_name, contact_phone, contact_email = self.get_contact_info()
    # purchase_order_number, ship_no_later_than, port_arrival_date, port_of_loading, port_of_destination = self.get_purchase_order_info()
    # shipment_type, incoterms, dist_method, order_data, order_group_id, page_number = self.get_order_meta_info()
    # final_destination = self.get_destination_info()
    # vendor = self.get_vendor_info()
    # total_value = self.get_total_value()
    # sku = self.get_sku_info()
    # pprint(self.text_cluster.get('cluster'))
    delivery_tables = self.get_delivery_tables()
    order_meta_info = self.get_order_meta_info()
    delivery_summary = self.get_delivery_summary()
    self.get_delivery_detail()
    self.template = {
      **order_meta_info,
      **delivery_summary,
      "delivery_tables": delivery_tables,
      "company_address": self.get_company_address(),
      "package_info": self.get_package_info(),
      # "company_phone": company_phone,
      # "company_fax": company_fax,
      # "contactName": contact_name,
      # "contactPhone": contact_phone,
      # "contactEmail": contact_email,
      "purchaseOrderNumber": self.get_purchase_order_number(),
      # "shipNoLaterThan": ship_no_later_than,
      # "portArrivalDate": port_arrival_date,
      # "portOfLoading": port_of_loading,
      # "portOfDestination": port_of_destination,
      # "shipmentType": shipment_type,
      # "incoterms": incoterms,
      # "distMethod": dist_method,
      # "orderData": order_data,
      # "orderGroupId": order_group_id,
      # "pageNumber": page_number,
      # "finalDestination": final_destination,
      "vendor": self.get_supplier_info(),
      "factory": self.get_factory_info(),
      # "totalValue": total_value,
      # "SKU": sku
    }
    return self.template