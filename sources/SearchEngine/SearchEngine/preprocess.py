import os
import re
from xml.dom.minidom import parse
import pickle
import json
from tqdm import tqdm
import thulac
from collections import defaultdict
import numpy as np

cutter = thulac.thulac(seg_only=True)

dir = "../../../"
base_path = [dir + item for item in ["xml_1", "xml_2", "xml_3"]]

def traverse(path, pattern, store):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            if pattern in item:
                store.append(item_path)
        else:
            traverse(item_path, pattern, store)

def read_all_doc_files(base):
    doc_files = []
    filename_cache = dir + "temp/filename.pkl"
    if os.path.exists(filename_cache):
        print('cache exist')
        doc_files = pickle.load(open(filename_cache, "rb"))
    else:
        print('cache not exist')
        for i, path in enumerate(base):
            traverse(path, ".xml", doc_files)
        pickle.dump(doc_files, open(filename_cache, "wb"))
    return doc_files

def construct_inverted_index(text_list, doc_num, inverted_index):
    for i, (term, offset) in enumerate(text_list):
        if doc_num not in inverted_index[term]:
            inverted_index[term][doc_num] = {"freq": 0, "offset": []}
        inverted_index[term][doc_num]["freq"] += 1
        inverted_index[term][doc_num]["offset"].append(offset)
    return inverted_index

def tag_offset(text_list):
    assert len(text_list[0]) == 2
    offset = 0
    for i in range(len(text_list)):
        text_list[i][1] = offset
        offset += len(text_list[i][0])
    return text_list

def calculate_BM25(inverted_index, doc_length):
    average_length = np.average(doc_length)
    total_doc = doc_length.shape[0]
    k = 2 # 超参数，限制tf对score的影响
    b = 0.5 # 超参数，控制文本长度对score的影响
    for term, term_docs in inverted_index.items():
        idf = np.log(total_doc / (len(term_docs) + 1)) # IDF值
        for doc, info in term_docs.items():
            tf = info["freq"] # TF值
            lp = 1 - b + b * doc_length[doc] / average_length # 长度惩罚项
            tfs = ((k + 1) * tf) / (k * lp + tf) # TF Score
            info["score"] = idf * tfs


if __name__ == "__main__":
    doc_files = read_all_doc_files(base_path)
    inverted_index = defaultdict(dict)
    # doc_files = doc_files[:1000]
    doc_files = [dir + item for item in doc_files]
    doc_length = np.zeros(len(doc_files)) # 记录文档长度(BM25用)
    with tqdm(total=len(doc_files), desc="Constructing Inverted Index") as pbar:
        for i, file in enumerate(doc_files):
            root = parse(file).documentElement
            full_text = root.getElementsByTagName("QW")
            if len(full_text) == 0:
                continue
            full_text = full_text[0].getAttribute("value")
            #print(full_text)
            full_text_list = cutter.cut(full_text)
            full_text_list = tag_offset(full_text_list)
            full_text_list = list(filter(lambda x: re.match(r"[0-9\u4e00-\u9af5]", x[0]) is not None, full_text_list))
            doc_length[i] = len(full_text_list)
            #print(full_text_list)
            inverted_index = construct_inverted_index(full_text_list, i, inverted_index)
            pbar.update(1)
    # 预计算BM25 Score
    calculate_BM25(inverted_index, doc_length)
    save_file = dir + "temp/inverted_index.json"

    with open(save_file, "w+", encoding="utf-8") as f:
        f.write(json.dumps(inverted_index, indent=2, ensure_ascii=False))
