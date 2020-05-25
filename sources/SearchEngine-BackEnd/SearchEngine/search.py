import json
import pickle
import thulac
import re
from xml.dom.minidom import parse
from cachetools import LRUCache
import numpy as np

root_dir = "../../../"
doc_files_store = root_dir + "temp/filename.pkl"
inverted_index_store = root_dir + "temp/inverted_index.json"
cutter = thulac.thulac(seg_only=True)

unpack_info = lambda ds, iis: (pickle.loads(open(ds, "rb").read()), json.loads(open(iis, "r+", encoding="utf-8").read()))

need_stats_keys = ["案件类别", "审判程序", "文书种类", "行政区划(省)", "结案年度"]

MAX_CACHE_SIZE = 1000
summary_cache = LRUCache(maxsize=MAX_CACHE_SIZE)
document_cache = LRUCache(maxsize=MAX_CACHE_SIZE)

def filters(doc_recall, condition, doc_files):
    if not condition:
        return doc_recall
    ret = []
    for doc in doc_recall:
        detail = get_single_detail(doc, doc_files, [])
        flag = True
        for key in condition:
            if key not in detail or detail[key] != condition[key]:
                flag = False
                break
        if flag:
            ret.append(doc)
    return ret

def recall(words, inverted_index):
    doc_recall = set()
    for word in words:
        if word not in inverted_index:
            continue
        for doc, info in inverted_index[word].items():
            doc = int(doc)
            doc_recall.add(doc)
    return list(doc_recall)

# def rank(doc_recall):
#     # rank第一关键字：出现的查询词数，第二关键字：出现查询词的词频
#     return [item[0] for item in sorted(list(doc_recall.items()), key=lambda x: (-x[1][0], -x[1][1]))]
def rank(doc_recall, words, inverted_index):
    local_doc_index = {doc : index for (index, doc) in enumerate(doc_recall)} # 方便计算分数用的
    scores = np.zeros(len(doc_recall))
    for word in words:
        if word not in inverted_index:
            continue
        for doc in doc_recall:
            if str(doc) not in inverted_index[word]:
                continue
            scores[local_doc_index[doc]] += inverted_index[word][str(doc)]["score"]
    doc_rank = [doc_recall[i] for i in scores.argsort()[::-1]]
    return doc_rank

def get_summary(doc_index, doc_files):
    # 根据索引获取文档内容
    rets = {}
    results = []
    statistics = {key: {} for key in need_stats_keys}
    for doc in doc_index:
        if doc not in summary_cache:
            item = {}
            item["index"] = doc
            root = parse(doc_files[doc]).documentElement
            normal_keys = ["WS", "CPSJ", "AJLB", "SPCX", "WSZL", "XZQH_P", "JAND"]
            # 文首，裁判时间，案件类别，审判程序，行政区划(省)
            for xml_key in normal_keys:
                elems = root.getElementsByTagName(xml_key)
                if len(elems) == 0:
                    continue
                key_cn = elems[0].getAttribute("nameCN")
                item[key_cn] = elems[0].getAttribute("value")
            summary_cache[doc] = item
        results.append(summary_cache[doc])
        item = summary_cache[doc]
        for key in need_stats_keys:
            if key not in item:
                continue
            statistics[key][item[key]] = 1 if item[key] not in statistics[key] else statistics[key][item[key]] + 1
    rets["results"] = results
    rets["statistics"] = statistics
    return rets

def get_single_detail(doc, doc_files, words):
    if doc in document_cache:
        return document_cache[doc]
    root = parse(doc_files[doc]).documentElement
    keys = ["WS", "JBFY", "AH", "CPSJ", "DSR", "DSRD", "SSJL", "AJJBQK", "AJJBQKD", "AJSSD", "CPFXGC", "QSFXD", "PJJG", "BSPJJG", "WW", "AJLB", "SPCX", "WSZL", "XZQH_P", "JAND"]
    # 文首，经办法院，案号，裁判时间，当事人，当事人段，诉讼记录，案件基本情况，案件基本情况段，案件事实段，裁判分析过程，起诉分析段，判决结果，本审判决结果，文尾，案件类别，审判程序，文书种类，行政区划(省)，结案年度
    escape_keys = {"AJLB", "SPCX", "WSZL", "XZQH_P", "JAND"}  # 不需要加格式的字段
    item = {}
    item["filename"] = doc_files[doc]
    for xml_key in keys:
        elems = root.getElementsByTagName(xml_key)
        if len(elems) == 0:
            continue
        # print(xml_key)
        key_cn = elems[0].getAttribute("nameCN")
        value = elems[0].getAttribute("value")
        item[key_cn] = value
    document_cache[doc] = item
    # print(document_cache[doc])
    return item


def main_loop(doc_files, inverted_index):
    while True:
        target = input("Input Search Keyword:")
        target = list(filter(lambda x: re.match(r"[0-9\u4e00-\u9af5]+", x) is not None, [item[0] for item in cutter.cut(target)]))
        doc_recall = recall(target, inverted_index)
        doc_index = rank(doc_recall)
        doc_content = get_summary(doc_index, doc_files)
        for i, content in enumerate(doc_content):
            print("Doc", doc_index[i])
            print(content)
        print("Find {} Items: {} / {}".format(len(doc_recall), doc_recall, doc_index))

if __name__ == "__main__":
    doc_files, inverted_index = unpack_info(doc_files_store, inverted_index_store)
    doc_files = [root_dir + file for file in doc_files]
    main_loop(doc_files, inverted_index)

