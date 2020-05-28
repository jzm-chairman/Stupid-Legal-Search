import json
import pickle
import thulac
import re
from xml.dom.minidom import parse
from cachetools import LRUCache
import numpy as np
import pymongo

root_dir = "../../../"
doc_files_store = root_dir + "temp/filename.pkl"
inverted_index_store = root_dir + "temp/inverted_index.json"
cutter = thulac.thulac(seg_only=True, filt=True)
client = pymongo.MongoClient(host="localhost", port=27017)
db = client['SearchEngine']
collection_paper = db['Paper']
collection_inverted_index = db['InvertedIndex']
need_stats_keys = ["案件类别", "审判程序", "文书种类", "行政区划(省)", "结案年度"]

# unpack_info = lambda ds, iis: (pickle.loads(open(ds, "rb").read()), json.loads(open(iis, "r+", encoding="utf-8").read()))

MAX_CACHE_SIZE = 1000
summary_cache = LRUCache(maxsize=MAX_CACHE_SIZE)
document_cache = LRUCache(maxsize=MAX_CACHE_SIZE)
# doc_files = [root_dir + file for file in pickle.loads(open(doc_files_store, "rb").read()]
cn_to_key = {'案件类别': 'AJLB', '审判程序': 'SPCX', '文书种类': 'WSZL', '行政区划(省)': 'XZQH_P', '结案年度': 'JAND',
             '裁判时间': 'CPSJ', '行政区划(市)': 'XZQH_C', '行政区划(区县)': 'XZQH_CC',
             '经办法院': 'JBFY', 'FGRYWZ': '法官人员完整'}

def get_inverted_index(term):
    return collection_inverted_index.find_one({'term': term})


def get_paper_info(pid):
    return collection_paper.find_one({'pid': pid})


def filters(doc_recall, condition):
    if not condition:
        return doc_recall
    ret = []
    for doc_id in doc_recall:
        doc_info = get_paper_info(doc_id)
        flag = True
        for cn_key in condition:
            if doc_info[cn_to_key[cn_key]] != condition[cn_key]:
                flag = False
                break
        if flag:
            ret.append(doc_info['pid'])
    return ret


def recall(words):
    doc_recall = set()
    for word in words:
        inverted_index = get_inverted_index(word)
        if inverted_index:
            for appear in inverted_index['appear_list']:
                doc_recall.add(appear['pid'])
    return list(doc_recall)


# def rank(doc_recall):
#     rank关键字BM25 score
#     返回pid列表
def rank(doc_recall, words):
    local_doc_index = {pid: index for (index, pid) in enumerate(doc_recall)} # 方便计算分数用的
    scores = np.zeros(len(doc_recall))
    for word in words:
        inverted_index = get_inverted_index(word)
        if inverted_index:
            for pid in doc_recall:
                for appear in inverted_index['appear_list']:
                    if appear['pid'] == pid:
                        scores[local_doc_index[pid]] += appear['score']
    doc_rank = [doc_recall[i] for i in scores.argsort()[::-1]]
    return doc_rank


def get_summary(pid_list):
    # 根据索引获取文档内容
    rets = {}
    results = []
    statistics = {key: {} for key in need_stats_keys}
    for pid in pid_list:
        item = {}
        if pid not in summary_cache:
            item['index'] = pid
            root = parse(get_paper_info(pid)['path']).documentElement
            normal_keys = ["WS", "CPSJ", "AJLB", "SPCX", "WSZL", "XZQH_P", "JAND"]
            # 文首，裁判时间，案件类别，审判程序，行政区划(省)
            for xml_key in normal_keys:
                elems = root.getElementsByTagName(xml_key)
                if len(elems) == 0:
                    continue
                key_cn = elems[0].getAttribute("nameCN")
                item[key_cn] = elems[0].getAttribute("value")
            summary_cache[pid] = item
        item = summary_cache[pid]
        results.append(item)
        for key in need_stats_keys:
            if key not in item:
                continue
            statistics[key][item[key]] = 1 if item[key] not in statistics[key] else statistics[key][item[key]] + 1
    rets["results"] = results
    rets["statistics"] = statistics
    return rets


def get_single_detail(doc, words):
    if doc in document_cache:
        return document_cache[doc]
    root = parse(get_paper_info(doc)['path']).documentElement
    keys = ["WS", "JBFY", "AH", "CPSJ", "DSR", "DSRD", "SSJL", "AJJBQK", "AJJBQKD", "AJSSD", "CPFXGC", "QSFXD", "PJJG", "BSPJJG", "WW", "AJLB", "SPCX", "WSZL", "XZQH_P", "JAND"]
    # 文首，经办法院，案号，裁判时间，当事人，当事人段，诉讼记录，案件基本情况，案件基本情况段，案件事实段，裁判分析过程，起诉分析段，判决结果，本审判决结果，文尾，案件类别，审判程序，文书种类，行政区划(省)，结案年度
    escape_keys = {"AJLB", "SPCX", "WSZL", "XZQH_P", "JAND"}  # 不需要加格式的字段
    item = {}
    item["filename"] = get_paper_info(doc)['path']
    for xml_key in keys:
        elems = root.getElementsByTagName(xml_key)
        if len(elems) == 0:
            continue
        key_cn = elems[0].getAttribute("nameCN")
        value = elems[0].getAttribute("value")
        item[key_cn] = value
    document_cache[doc] = item
    return item


def main_loop():
    while True:
        target = input("Input Search Keyword:")
        target = list(filter(lambda x: re.match(r"[0-9\u4e00-\u9af5]+", x) is not None, [item[0] for item in cutter.cut(target)]))
        doc_recall = recall(target)
        doc_index = rank(doc_recall)
        doc_content = get_summary(doc_index)
        for i, content in enumerate(doc_content):
            print("Doc", doc_index[i])
            print(content)
        print("Find {} Items: {} / {}".format(len(doc_recall), doc_recall, doc_index))


if __name__ == "__main__":
    # doc_files, inverted_index = unpack_info(doc_files_store, inverted_index_store)
    main_loop()
