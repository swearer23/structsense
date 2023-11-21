from Parser.base import BasePOContract

class WoolWorthsGroupPOContract(BasePOContract):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def get_company_address(self):
    address = self.text_cluster.get('cluster').get(0)
    return " ".join([x.strip() for x in address]).strip()
  
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
  
  def get_order_meta_info(self):
    order_meta_info = self.text_cluster.get('cluster').get(7)
    order_meta_info = [order_meta_info[i] + order_meta_info[i + 1] for i in range(0, len(order_meta_info) - 1, 2)]
    shipment_type = order_meta_info[0].split(':')[-1].strip()
    incoterms = order_meta_info[1].split(':')[-1].strip()
    dist_method = order_meta_info[2].split(':')[-1].strip()
    order_data = order_meta_info[3].split(':')[-1].strip()
    order_group_id = order_meta_info[4].split(':')[-1].strip()
    page_number = order_meta_info[5].split(':')[-1].strip()
    return shipment_type, incoterms, dist_method, order_data, order_group_id, page_number
  
  def get_destination_info(self):
    destination_info = self.text_cluster.get('cluster').get(4)
    return " ".join(destination_info)
  
  def get_vendor_info(self):
    vendor_info = self.text_cluster.get('cluster').get(5)
    return " ".join(vendor_info).split(':')[1].strip()
  
  def parse(self, *args, **kwargs):
    company_phone, company_fax = self.get_company_contact_info()
    contact_name, contact_phone, contact_email = self.get_contact_info()
    purchase_order_number, ship_no_later_than, port_arrival_date, port_of_loading, port_of_destination = self.get_purchase_order_info()
    shipment_type, incoterms, dist_method, order_data, order_group_id, page_number = self.get_order_meta_info()
    final_destination = self.get_destination_info()
    vendor = self.get_vendor_info()
    self.template = {
      "company_address": self.get_company_address(),
      "company_phone": company_phone,
      "company_fax": company_fax,
      "contactName": contact_name,
      "contactPhone": contact_phone,
      "contactEmail": contact_email,
      "purchaseOrderNumber": purchase_order_number,
      "shipNoLaterThan": ship_no_later_than,
      "portArrivalDate": port_arrival_date,
      "portOfLoading": port_of_loading,
      "portOfDestination": port_of_destination,
      "shipmentType": shipment_type,
      "incoterms": incoterms,
      "distMethod": dist_method,
      "orderData": order_data,
      "orderGroupId": order_group_id,
      "pageNumber": page_number,
      "finalDestination": final_destination,
      "vendor": vendor,
    }
    return self.template