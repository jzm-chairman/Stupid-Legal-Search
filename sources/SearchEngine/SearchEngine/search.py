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

MAX_CACHE_SIZE = 1000
summary_cache = LRUCache(maxsize=MAX_CACHE_SIZE)
document_cache = LRUCache(maxsize=MAX_CACHE_SIZE)

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

def get_content(doc_index, doc_files):
    # 根据索引获取文档内容
    result = []
    for doc in doc_index:
        if doc not in summary_cache:
            item = {}
            item["internal_index"] = doc
            root = parse(doc_files[doc]).documentElement
            normal_keys = {"title": "WS", "content": "QW", "category": "AJLX", "time": "CPSJ"}
            for result_key, xml_key in normal_keys.items():
                elems = root.getElementsByTagName(xml_key)
                if len(elems) == 0:
                    continue
                item[result_key] = elems[0].getAttribute("value")
            summary_cache[doc] = item
        result.append(summary_cache[doc])
    return result

def get_single_detail(doc, doc_files):
    if doc in document_cache:
        return document_cache[doc]
    root = parse(doc_files[doc]).documentElement
    keys = ["WS", "JBFY", "AH", "CPSJ", "DSR", "SSJL", "AJJBQK", "CPFXGC", "PJJG", "WW"]
    item = {}
    for xml_key in keys:
        elems = root.getElementsByTagName(xml_key)
        if len(elems) == 0:
            continue
        key_cn = elems[0].getAttribute("nameCN")
        value = elems[0].getAttribute("value")
        item[key_cn] = value
    document_cache[doc] = item
    return item


def main_loop(doc_files, inverted_index):
    while True:
        target = input("Input Search Keyword:")
        target = list(filter(lambda x: re.match(r"[0-9\u4e00-\u9af5]+", x) is not None, [item[0] for item in cutter.cut(target)]))
        doc_counter = recall(target, inverted_index)
        doc_index = rank(doc_counter)
        doc_content = get_content(doc_index, doc_files)
        for i, content in enumerate(doc_content):
            print("Doc", doc_index[i])
            print(content)
        print("Find {} Items: {} / {}".format(len(doc_counter), doc_counter, doc_index))

if __name__ == "__main__":
    doc_files, inverted_index = unpack_info(doc_files_store, inverted_index_store)
    doc_files = [root_dir + file for file in doc_files]
    main_loop(doc_files, inverted_index)

