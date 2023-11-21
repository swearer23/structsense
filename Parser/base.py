from itertools import chain

class ParserBaseClass:
  def __init__(self, text_cluster, *args, **kwargs):
    self.text_cluster = text_cluster
    self.flat_blocks_text = self.flatten_blocks_text()

  def parse(self, *args, **kwargs):
    raise NotImplementedError
  
  def flatten_blocks_text(self):
    return list(chain.from_iterable(self.text_cluster.get('blocks_text')))
  
class BasePOContract(ParserBaseClass):
  def __init__(self, text_cluster, *args, **kwargs):
    super().__init__(text_cluster, *args, **kwargs)
  
  def parse(self, *args, **kwargs):
    raise NotImplementedError