import fitz
from pprint import pprint
from sklearn.cluster import DBSCAN

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

def get_text_cluster(pdf_path):
  # 打开PDF文件
  pdf = fitz.open(pdf_path)
  words = extract_words(pdf)
  pdf.close()
  features = define_features(words)
  clusters = get_clusters(features, words, eps=100)
  return clusters

if __name__ == '__main__':
  clusters = get_text_cluster("./docs/PO.PDF")
  pprint(clusters)
