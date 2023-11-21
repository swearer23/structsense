from get_text_cluster import get_text_cluster
from Parser.woolworths_group import WoolWorthsGroupPOContract
from pprint import pprint

def main(pdf_path):
  clusters = get_text_cluster(pdf_path)
  pprint(clusters)
  result = WoolWorthsGroupPOContract(clusters).parse()
  return result

if __name__ == '__main__':
  pdf_path = './docs/PO.PDF'
  key_info = main(pdf_path)
  pprint(key_info)