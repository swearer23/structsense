from get_text_cluster import get_text_cluster
from Parser.woolworths_group import WoolWorthsGroupPOContract
from Parser.primark import PrimarkPOContract
from pprint import pprint

def main(pdf_path, clsname='WoolWorthsGroupPOContract'):
  clusters, pdf_meta = get_text_cluster(pdf_path, eps=30)
  result = globals()[clsname](clusters, pdf_meta).parse()
  return result

if __name__ == '__main__':
  # pdf_path = './docs/PurchaseOrder47648175.PDF'
  # key_info = main(pdf_path)
  pdf_path = './docs/PO1077867-0.PDF'
  key_info = main(pdf_path, 'PrimarkPOContract')
  # pprint(key_info)