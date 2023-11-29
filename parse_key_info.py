from get_text_cluster import get_text_cluster
from Parser.woolworths_group import WoolWorthsGroupPOContract
from Parser.primark import PrimarkPOContract
from pprint import pprint

def parse(pdf_path, clsname='WoolWorthsGroupPOContract', eps=100):
  clusters, pdf_meta = get_text_cluster(pdf_path, eps)
  result = globals()[clsname](clusters, pdf_meta).parse()
  return result

if __name__ == '__main__':
  # pdf_path = './docs/PurchaseOrder47648175.PDF'
  # key_info = parse(pdf_path, eps=100)
  pdf_path = './docs/PO1077867-0.PDF'
  key_info = parse(pdf_path, 'PrimarkPOContract', eps=30)
  pprint(key_info)
