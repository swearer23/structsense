import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# 加载Spacy的英文模型
nlp = spacy.load("en_core_web_sm")

# 输入的文本示例
texts = [
    "1 Woolworths Way Phone : (02)8885 0000 PURCHASE ORDER NO : 47648106",
    "BELLA VISTA NSW 2153 Fax : (02)8885 9001 SHIP NO LATER THAN : 20 APR 2024 AUSTRALIA",
    "www.woolworths.com.au PORT ARRIVAL DATE : 23 MAY 2024",
    "CONTACT: Nick Allan PORT OF LOADING : CNNGB",
    "PHONE: 0452381466 PORT OF DESTINATION : AUBNE",
    "EMAIL:: nallan1@bigw.com FINAL 0290 VENDOR: 98401478 SHIPMENT TYPE : SEA"
    # 添加更多文本...
]

# 对文本进行处理并提取实体
entities = []
for text in texts:
    doc = nlp(text)
    entities.append(" ".join([ent.text for ent in doc.ents]))  # 提取命名实体

# 使用TF-IDF向量化实体特征
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(entities)

# 使用K均值聚类
num_clusters = 2  # 指定群组数量，您可以根据需要调整
kmeans = KMeans(n_clusters=num_clusters)
kmeans.fit(X)

# 输出文本聚类结果
for i in range(num_clusters):
    cluster_texts = []
    for j, label in enumerate(kmeans.labels_):
        if label == i:
            cluster_texts.append(texts[j])
    print(f"Cluster {i + 1}:\n{cluster_texts}\n")
