import os
import re
from xml.dom.minidom import parse
import pickle
from tqdm import tqdm
import thulac
from random import shuffle
# import mongoengine
from collections import defaultdict
import numpy as np
import pymongo
import sys

cutter = thulac.thulac(seg_only=True, filt=True)

# dir = "../../../" # change it for data file path
dir = "D:\\Stupid-Legal-Search\\dataset\\"
# dir = 'E:\\Tsinghua\\2020_spring\\SearchEngine\\Project\\' # 使用绝对路径
base_path = [dir + item for item in ["xml_1", "xml_2", "xml_3", "xml_4"]]


def traverse(path, pattern, store):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            if pattern in item:
                store.append(item_path)
                global file_num
                file_num += 1
                if file_num % 1000 == 0:
                    print('file_num: {}'.format(file_num))
        else:
            traverse(item_path, pattern, store)


def read_all_doc_files(base):
    global file_num
    file_num = 0
    doc_files = []
    filename_cache = dir + "temp/filename.pkl"
    if os.path.exists(filename_cache):
        print('cache exist')
        doc_files = pickle.load(open(filename_cache, "rb"))
    else:
        print('cache not exist')
        if not os.path.exists(dir + "temp"):
            os.mkdir(dir + "temp")
        for i, path in enumerate(base):
            print('traverse @ ' + str(i))
            traverse(path, ".xml", doc_files)
        print('#File: ' + str(len(doc_files)))
        pickle.dump(doc_files, open(filename_cache, "wb"))
    return doc_files


def update_inverted_index(text_list, doc_num, inverted_index_dict, appear_list):
    appear_dict = {}
    for term, _ in text_list:
        if term not in appear_dict.keys():
            appear_dict[term] = {'pid': doc_num, 'freq': 0, 'score': 0}
        appear_dict[term]['freq'] += 1
    global appear_num
    for (term, appear) in appear_dict.items():
        appear_list += [appear]
        inverted_index_dict[term] += [appear_num]
        appear_num += 1


def tag_offset(text_list):
    assert len(text_list[0]) == 2
    offset = 0
    for i in range(len(text_list)):
        text_list[i][1] = offset
        offset += len(text_list[i][0])
    return text_list


def get_BM25(tf, doc_len, avg_len, total_doc, term_doc):
    idf = np.log(total_doc / (term_doc + 1))
    k = 2 # 超参数，限制tf对score的影响
    b = 0.5 # 超参数，控制文本长度对score的影响
    lp = 1 - b + b * doc_len / avg_len # 长度惩罚项
    tfs = ((k + 1) * tf) / (k * lp + tf) # TF Score
    return idf * tfs


def trim_and_cut(text):
    text = re.split(r"[^0-9\u4e00-\u9af5]", text)
    return text


def parse_paper(file_path, pid):
    label_elements = ['AJLB', 'SPCX', 'WSZL', 'CPSJ', 'JAND', 'XZQH_P', 'XZQH_C', 'XZQH_CC', 'JBFY', 'FGRYWZ', 'WS']
    paper_dict = {}
    try:
        root = parse(file_path).documentElement
        full_text = root.getElementsByTagName("QW")
    except Exception:
        return None, None
    if len(full_text) == 0:
        return None, None
    full_text = full_text[0].getAttribute("value")

    paper_dict['path'] = file_path
    paper_dict['pid'] = pid
    for label in label_elements:
        try:
            if label == 'FGRYWZ':
                paper_dict[label] = [x.getAttribute("value") for x in root.getElementsByTagName(label)]
            else:
                paper_dict[label] = root.getElementsByTagName(label)[0].getAttribute("value")
        except Exception:
            paper_dict[label] = ''
    return full_text, paper_dict


def extract_appearance_and_labels(db, doc_files):
    collection_paper = db['Paper']
    appear_list = []
    paper_list = []
    inverted_index_dict = defaultdict(list)
    doc_length = np.zeros(len(doc_files)) # 记录文档长度(BM25用)
    offset_size = 0
    global appear_num
    appear_num = 0
    paper_num = 0
    with tqdm(total=len(doc_files), desc="Extracting Appearances and Labels") as pbar:
        for i, file in enumerate(doc_files):
            full_text, paper_dict = parse_paper(file, paper_num)
            if full_text is None:
                pbar.update(1)
                continue
            paper_num += 1
            paper_list.append(paper_dict)
            seg_list = trim_and_cut(full_text)
            full_text_list = []
            for seg_text in seg_list:
                full_text_list += cutter.cut(seg_text)
            doc_length[i] = len(full_text_list)
            offset_size += len(full_text_list)

            update_inverted_index(full_text_list, i, inverted_index_dict, appear_list)
            if len(paper_list) > 10000 or pbar.n + 1 == pbar.total:
                print("insert_many Paper")
                collection_paper.insert_many(paper_list)
                paper_list = []
            if (i + 1) % 100 == 0:
                print("offset_size: " + str(offset_size))
                print("appear_num: " + str(appear_num))
                print("term_num: " + str(len(inverted_index_dict.keys())))
                print("paper_num: " + str(paper_num))
            pbar.update(1)
    return doc_length, inverted_index_dict, appear_list


def construct_inverted_index(db, doc_length, inverted_index_dict, appear_list):
    collection_inverted_index = db['InvertedIndex']
    wait_list = []
    avg_doc_len = np.average(doc_length)
    total_doc = len(doc_length)
    appear_cnt = 0
    with tqdm(total=len(inverted_index_dict.keys()), desc="Constructing Inverted Index") as pbar:
        for term, appear_id_list in inverted_index_dict.items():
            inverted_index = {'term': term, 'appear_list': []}
            for aid in appear_id_list:
                appear = appear_list[aid]
                score = get_BM25(appear['freq'], doc_length[appear['pid']], avg_doc_len, total_doc, len(appear_id_list))
                appear['score'] = score
                inverted_index['appear_list'].append(appear)
                appear_cnt += 1
            wait_list.append(inverted_index)
            if len(wait_list) > 5000 or pbar.n + 1 == pbar.total:
                print("insert_many InvertedIndex")
                collection_inverted_index.insert_many(wait_list)
                wait_list = []
            pbar.update(1)


if __name__ == "__main__":
    doc_files = read_all_doc_files(base_path)
    # shuffle(doc_files)
    doc_files = [item for item in doc_files]
    doc_files = doc_files[:10000]
    print('#File: ' + str(len(doc_files)))

    client = pymongo.MongoClient(host="localhost", port=27017)
    db = client['SearchEngine']

    # extract_paper_labels(db, doc_files)
    doc_length, inverted_index_dict, appear_list = extract_appearance_and_labels(db, doc_files)
    construct_inverted_index(db, doc_length, inverted_index_dict, appear_list)
