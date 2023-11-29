from itertools import chain

class RawBlock:
  def __init__(self, raw_block) -> None:
    self.raw_block = raw_block

  def get_text(self):
    return self.raw_block[4: -3][0]
  
  def get_y_0(self):
    return self.raw_block[1]
  
  def get_y_1(self):
    return self.raw_block[3]
  
  def get_page(self):
    return self.raw_block[-1]
  
  def __repr__(self,) -> str:
    return f"RawBlock({self.raw_block})"

class ParserTableList(list):
  def __init__(self, *args, **kwargs):
    super().__init__([
      ParserTable(x) for x in args[0]
    ], **kwargs)
  
  def get_first_table_after_rect(self, raw_block):
    for table in self:
      if table.rect[1] > raw_block.get_y_1() and table.page == raw_block.get_page():
        return table
    return None
  
class ParserTable:
  def __init__(self, table, *args, **kwargs):
    self.df = table['pd']
    self.rect = table['rect']
    self.page = table['page']

  def __repr__(self) -> str:
    return f"ParserTable({self.df})"

class ParserBaseClass:
  def __init__(self, text_cluster, pdf_meta, *args, **kwargs):
    self.text_cluster = text_cluster
    self.pdf_meta = pdf_meta
    self.flat_blocks_text = self.flatten_blocks_text()
    self.tables = ParserTableList(self.text_cluster.get('tables'))
    self.blocks = [RawBlock(x) for x in self.text_cluster.get('raw_blocks')]

  def parse(self, *args, **kwargs):
    raise NotImplementedError
  
  def flatten_blocks_text(self):
    return list(chain.from_iterable(self.text_cluster.get('blocks_text')))
  
class BasePOContract(ParserBaseClass):
  def __init__(self, text_cluster, pdf_meta, *args, **kwargs):
    super().__init__(text_cluster, pdf_meta, *args, **kwargs)
  
  def parse(self, *args, **kwargs):
    raise NotImplementedError
  
  def parse_to_schema(self):
    raise NotImplementedError