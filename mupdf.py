import fitz  # PyMuPDF
from pprint import pprint
from sklearn.cluster import DBSCAN

# 打开PDF文件
pdf_document = "./docs/PO.PDF"  # 替换为您的PDF文件路径
pdf = fitz.open(pdf_document)

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
# pprint(words)
pdf.close()

font_list = list(set([x.get('font') for x in words]))
features = [
    (
        x['bbox'][0] - x['blockbbox'][0],
        x['bbox'][1] - x['blockbbox'][1],
        x['bbox'][2] - x['blockbbox'][0],
        x['bbox'][3] - x['blockbbox'][1],
        x['size'] * 1000,
        x['color'] * 1000,
        x['fontflag'] * 1000,
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

words_map = {}

for index, word in enumerate(words):
    words_map[hash(features[index])] = words[index]

dbscan = DBSCAN(eps=100, min_samples=2)  # 可根据实际情况调整eps和min_samples
dbscan.fit(features)

labels = dbscan.labels_
# print(labels)
# exit()
clusters = {}
for i, label in enumerate(labels):
    if label not in clusters:
        clusters[label] = []
    clusters[label].append(features[i])

for i, cluster in clusters.items():
    print(f"============Cluster {i if i != -1 else 'Noise'} Text Features:")
    for text_feature in cluster:
        print(words_map[hash(text_feature)].get('text'))
        # print(text_feature)
    print("\n")