import json
import pickle
import thulac
import re
from xml.dom.minidom import parse
from cachetools import LRUCache

root_dir = "../../../"
doc_files_store = root_dir + "temp/filename.pkl"
inverted_index_store = root_dir + "temp/inverted_index.json"
cutter = thulac.thulac(seg_only=True)

unpack_info = lambda ds, iis: (pickle.loads(open(ds, "rb").read()), json.loads(open(iis, "r+", encoding="utf-8").read()))

need_stats_keys = ["案件类别", "审判程序", "文书种类", "行政区划(省)", "结案年度"]

MAX_CACHE_SIZE = 1000
summary_cache = LRUCache(maxsize=MAX_CACHE_SIZE)
document_cache = LRUCache(maxsize=MAX_CACHE_SIZE)

def filters(doc_counter, condition, doc_files):
    ret = {}
    for doc in doc_counter:
        detail = get_single_detail(doc, doc_files)
        flag = True
        for key in condition:
            if detail[key] != condition[key]:
                flag = False
                break
        if flag:
            ret[doc] = doc_counter[doc]
    return ret

def recall(words, inverted_index):
    doc_counter = {}
    words = set(words)
    for word in words:
        if word not in inverted_index:
            continue
        for doc, info in inverted_index[word].items():
            doc = int(doc)
            if doc not in doc_counter:
                doc_counter[doc] = [0, 0]  # [出现的查询词数，出现查询词的词频]
            doc_counter[doc][0] += 1
            doc_counter[doc][1] += info["freq"]
    return doc_counter

def rank(doc_counter):
    # rank第一关键字：出现的查询词数，第二关键字：出现查询词的词频
    return [item[0] for item in sorted(list(doc_counter.items()), key=lambda x: (-x[1][0], -x[1][1]))]

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
            statistics[key][item[key]] = 1 if item[key] not in statistics[key] else statistics[key][item[key]] + 1
    rets["results"] = results
    rets["statistics"] = statistics
    return rets

def get_single_detail(doc, doc_files):
    if doc in document_cache:
        return document_cache[doc]
    root = parse(doc_files[doc]).documentElement
    keys = ["WS", "JBFY", "AH", "CPSJ", "DSR", "SSJL", "AJJBQK", "CPFXGC", "PJJG", "BSPJJG", "WW", "AJLB", "SPCX", "WSZL", "XZQH_P", "JAND"]
    # 文首，经办法院，案号，裁判时间，当事人，诉讼记录，案件基本情况，裁判分析过程，判决结果，本审判决结果，文尾，案件类别，审判程序，行政区划(省)，结案年度
    item = {}
    for xml_key in keys:
        elems = root.getElementsByTagName(xml_key)
        if len(elems) == 0:
            continue
        key_cn = elems[0].getAttribute("nameCN")
        value = elems[0].getAttribute("value")
        if xml_key != "WS":
            value = value.strip().replace(" ", "<br>")
        item[key_cn] = value
    document_cache[doc] = item
    return item


def main_loop(doc_files, inverted_index):
    while True:
        target = input("Input Search Keyword:")
        target = list(filter(lambda x: re.match(r"[0-9\u4e00-\u9af5]+", x) is not None, [item[0] for item in cutter.cut(target)]))
        doc_counter = recall(target, inverted_index)
        doc_index = rank(doc_counter)
        doc_content = get_summary(doc_index, doc_files)
        for i, content in enumerate(doc_content):
            print("Doc", doc_index[i])
            print(content)
        print("Find {} Items: {} / {}".format(len(doc_counter), doc_counter, doc_index))

if __name__ == "__main__":
    doc_files, inverted_index = unpack_info(doc_files_store, inverted_index_store)
    doc_files = [root_dir + file for file in doc_files]
    main_loop(doc_files, inverted_index)

