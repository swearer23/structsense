import os
import importlib
from parse_key_info import parse

# loop every file in the folder
folder_name = './docs/WoolWorthsGroupPOContract/'
for filename in os.listdir(folder_name):
  if filename.lower().endswith(".pdf"):
      print(filename)
      local_filename = folder_name + filename
      key_info = parse(local_filename, 'WoolWorthsGroupPOContract')
      module = importlib.import_module('SchemaParser.WoolWorthsGroupPOContract')
      po_main, po_details, raw_info = module.parse_to_u8_schema(key_info)
      print(po_main)
  else:
      continue
