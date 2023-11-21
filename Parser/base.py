class ParserBaseClass:
  def __init__(self, text_cluster, *args, **kwargs):
    self.text_cluster = text_cluster

  def parse(self, *args, **kwargs):
    raise NotImplementedError
  
class BasePOContract(ParserBaseClass):
  def __init__(self, text_cluster, *args, **kwargs):
    super().__init__(text_cluster, *args, **kwargs)
  
  def parse(self, *args, **kwargs):
    raise NotImplementedError