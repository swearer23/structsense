import fitz
from pprint import pprint
from sklearn.cluster import DBSCAN

def get_raw_blocks(pdf: fitz.Document):
  blocks = []
  for page_num in range(pdf.page_count):
    page = pdf.load_page(page_num)
    blocks.extend([[
      *x, page_num
    ] for x in page.get_text("blocks")])

  blocks_text = [list(t[4:-3]) for t in blocks]
  return blocks, blocks_text, 

def get_table_cluster(pdf: fitz.Document):
  pd_tables = []
  for page_num in range(pdf.page_count):
    page = pdf.load_page(page_num)
    table_finder = page.find_tables(
      snap_y_tolerance=3,
      snap_x_tolerance=1,
      text_y_tolerance=3,
      text_x_tolerance=3,
      join_tolerance=3,
      join_y_tolerance=3,
      intersection_x_tolerance=1
    )
    for table in table_finder.tables:
      pd_tables.append({
        "pd": table.to_pandas(),
        "rect": table.bbox,
        "page": page_num
      })
  return pd_tables

def get_clusters(features, words, eps=100, min_samples=2):
  words_map = {}

  for index in range(len(words)):
    words_map[hash(features[index])] = words[index]

  dbscan = DBSCAN(eps=eps, min_samples=min_samples)  # 可根据实际情况调整eps和min_samples
  dbscan.fit(features)

  labels = dbscan.labels_
  clusters = {
    'noise': [],
    'cluster': {}
  }
  for i, label in enumerate(labels):
    text = words_map[hash(features[i])].get('text')
    if label == -1:
       clusters['noise'].append(text)
    else:
      if label not in clusters['cluster']:
        clusters['cluster'][label] = []
      clusters['cluster'][label].append(text)
  
  return clusters

def define_features(words):
  font_list = list(set([x.get('font') for x in words]))
  features = [
      (
          x['bbox'][0] - x['blockbbox'][0],
          x['bbox'][1] - x['blockbbox'][1],
          x['bbox'][2] - x['blockbbox'][0],
          x['bbox'][3] - x['blockbbox'][1],
          x['size'] * 100,
          x['color'] * 100,
          x['fontflag'] * 10,
          font_list.index(x['font']),
          # x['linebbox'][0],
          # x['linebbox'][1],
          # x['linebbox'][2],
          # x['linebbox'][3],
          x['blockbbox'][0],
          x['blockbbox'][1],
          x['blockbbox'][2],
          x['blockbbox'][3],
      ) for x in words
  ]
  return features

def extract_words(pdf):
  words = []
  # 遍历每一页
  for page_num in range(pdf.page_count):
    page = pdf.load_page(page_num)

    # 提取文本块信息
    blocks = [x for x in page.get_text("dict").get('blocks') if x.get('type') == 0]  # 获取每个文本块的信息
    for b in blocks:
      lines = b.get('lines')
      for line in lines:
        spans = line.get('spans')
        for span in spans:
          words.append({
            'text': span.get('text'),
            'font': span.get('font'),
            'size': span.get('size'),
            'bbox': span.get('bbox'),
            'color': span.get('color'),
            'linebbox': line.get('bbox'),
            'blockbbox': b.get('bbox'),
            'fontflag': b.get('flags', 0),
          })
  return words

def get_text_cluster(pdf_path, eps=100):
  # 打开PDF文件
  pdf = fitz.open(pdf_path)
  words = extract_words(pdf)
  features = define_features(words)
  clusters = get_clusters(features, words, eps)
  clusters['tables'] = get_table_cluster(pdf)
  clusters['raw_blocks'], clusters['blocks_text'] = get_raw_blocks(pdf)
  pdf_meta = {
    "width": pdf.load_page(0).rect.width,
    "height": pdf.load_page(0).rect.height,
  }
  pdf.close()
  return clusters, pdf_meta

if __name__ == '__main__':
  clusters, pdf_meta = get_text_cluster("./docs/PO.PDF")
  pprint(clusters, pdf_meta)
