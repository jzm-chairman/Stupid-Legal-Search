import json
import pickle
import thulac
import re
from xml.dom.minidom import parse
from cachetools import LRUCache
import numpy as np
import pymongo
import random
from functools import reduce
import time
from .utils import *
from threading import Thread

root_dir = "../../../"
# doc_files_store = root_dir + "temp/filename.pkl"
inverted_index_store = root_dir + "temp/inverted_index.json"
cutter = thulac.thulac(seg_only=True, filt=True)
client = pymongo.MongoClient(host="localhost", port=27017)
db = client['SearchEngine']
# db = client['SearchTest']
collection_paper = db['Paper']
collection_inverted_index = db['InvertedIndex']
collection_trie = db['Trie']
# need_stats_keys = ["案件类别", "审判程序", "文书种类", "行政区划(省)", "结案年度"]
need_stats_keys = ["AJLB", "SPCX", "WSZL", "XZQH_P", "JAND", "LB"]
emb_file = root_dir + 'word_embedding\\sgns.renmin.word'
# emb = Embedding(emb_file)

# unpack_info = lambda ds, iis: (pickle.loads(open(ds, "rb").read()), json.loads(open(iis, "r+", encoding="utf-8").read()))

MAX_CACHE_SIZE = 200000
# summary_cache = LRUCache(maxsize=MAX_CACHE_SIZE)
document_cache = LRUCache(maxsize=MAX_CACHE_SIZE)
# doc_files = [root_dir + file for file in pickle.loads(open(doc_files_store, "rb").read()]
cn_to_key = {'案件类别': 'AJLB', '审判程序': 'SPCX', '文书种类': 'WSZL', '行政区划(省)': 'XZQH_P', '结案年度': 'JAND',
             '裁判时间': 'CPSJ', '行政区划(市)': 'XZQH_C', '行政区划(区县)': 'XZQH_CC',
             '经办法院': 'JBFY', '法官人员完整': 'FGRYWZ', '文首': 'WS', '法律法条分组': 'FLFTFZ',
             '案例类别': 'LB', '全文': 'QW', '案例原则': 'ALYZ', '标题': 'title'}
key_to_cn = {value : key for key, value in cn_to_key.items()}

# inverted_index_all = {item["term"] : {"appear_list": item["appear_list"]} for item in collection_inverted_index.find()}
# print("Inverted Index Size:", len(inverted_index_all))

# 加速：一次性将数据库文档部分装入内存
all_paper_info = collection_paper.find()
summary_cache = {item["pid"] : {**{key_to_cn[key] : item[key] for key in key_to_cn if key in item}, **{"index" : item["pid"]}} for item in all_paper_info}

scan_times = 0
def async_scan_files(doc_list):
    global scan_times
    scan_times += 1
    local_times = scan_times
    print("Start Prefetch:", local_times)
    for doc in doc_list:
        get_single_detail(doc)
    print("Prefetch Documents Done:", local_times)

def get_inverted_index(term):
    return collection_inverted_index.find_one({'term': term})
    # try:
    #     return inverted_index_all[term]
    # except KeyError as e:
    #     return None

def get_paper_info(pid):
    return collection_paper.find_one({'pid': pid})

def query_by_condition(condition, doc_list=None):
    cond = {cn_to_key[key] : value for key, value in condition.items()}
    cond_index = {"pid": {"$in": doc_list}} if doc_list is not None else {}
    return collection_paper.find({**cond_index, **cond}, {"_id": 0, "pid": 1, "WS": 1})
    # return collection_paper.find(cond, {"_id": 0, "pid": 1})

def filters(doc_recall, condition):
    if not condition:
        return doc_recall
    cursor = query_by_condition(condition, doc_recall)
    # ret = list(set(doc_recall) & {item["pid"] for item in cursor})
    ret = [item["pid"] for item in cursor]
    print('Filter len: {}'.format(len(ret)))
    return ret


def recall(words):
    doc_recall = set()
    for word in words:
        inverted_index = get_inverted_index(word)
        if inverted_index:
            for appear in inverted_index['appear_list']:
                doc_recall.add(appear['pid'])
    return list(doc_recall)


MAX_RANK_CACHE_SIZE = 100
rank_cache = LRUCache(maxsize=MAX_RANK_CACHE_SIZE)
# def rank(doc_recall):
#     rank关键字BM25 score
#     返回pid列表


def rank(doc_recall, words, rank_key):
    rank_cache_key = reduce(lambda x, y: x + y, map(str, rank_key))
    if rank_cache_key in rank_cache:
        return rank_cache[rank_cache_key]
    local_doc_index = {pid: index for (index, pid) in enumerate(doc_recall)} # 方便计算分数用的
    scores = np.zeros(len(doc_recall))
    word_appear_list = []
    pt_list = []
    for word in words:
        word_appear_list += [get_inverted_index(word)['appear_list']]
        pt_list += [0]
    for pid in doc_recall:
        new_pt_list = []
        for pt, appear_list in zip(pt_list, word_appear_list):
            while pt < len(appear_list) and appear_list[pt]['pid'] < pid:
                pt += 1
            if pt < len(appear_list) and appear_list[pt]['pid'] == pid:
                scores[local_doc_index[pid]] += appear_list[pt]['score']
            new_pt_list += [pt]
        pt_list = new_pt_list
    doc_rank = [doc_recall[i] for i in scores.argsort()[::-1]]
    rank_cache[rank_cache_key] = doc_rank
    return doc_rank


def get_meta_info(pid_list):
    # 根据索引获取文档内容
    normal_keys = ["LB", "title", "WS", "CPSJ", "AJLB", "SPCX", "WSZL", "XZQH_P", "JAND"]
    # 文首，裁判时间，案件类别，审判程序，文书种类，行政区划(省)，结案年度
    rets = {}
    results = []
    statistics = {key_to_cn[key]: {} for key in need_stats_keys}
    for pid in pid_list:
        if pid not in summary_cache:
            paper_info = get_paper_info(pid)
            if paper_info is None:
                continue
            item = {key_to_cn[key] : paper_info[key] for key in normal_keys}
            item["index"] = pid
            summary_cache[pid] = item
        item = summary_cache[pid]
        results.append(item)
        for key in need_stats_keys:
            key = key_to_cn[key]
            if key not in item or not item[key]:
                continue
            if isinstance(item[key], list):
                for subitem in item[key]:
                    statistics[key][subitem] = 1 if subitem not in statistics[key] else statistics[key][subitem] + 1
            else:
                statistics[key][item[key]] = 1 if item[key] not in statistics[key] else statistics[key][item[key]] + 1
    rets["results"] = results
    rets["statistics"] = statistics
    return rets


def get_best_word(node):
    def update_score(node):
        node['max_score'] = 0 if node['at'] == 0 else node['score']
        for child in node['children']:
            if child['cnt'] > 0:
                node['max_score'] = max(node['max_score'], child['max_score'])
    res = None
    if node['at'] > 0 and node['score'] == node['max_score']:
        node['at'] -= 1
        res = ''
    else:
        for child in node['children']:
            if child['cnt'] > 0 and child['max_score'] == node['max_score']:
                res = child['char'] + get_best_word(child)
                break
    if res is not None:
        node['cnt'] -= 1
        update_score(node)
    return res


def get_recommended_words(prefix):
    if prefix == '':
        return []
    node = collection_trie.find_one({'char': prefix[0]})
    if node is None:
        return []
    print('prefix: {}'.format(prefix))
    for c in list(prefix[1:]):
        find = False
        for child_dict in node['children']:
            if child_dict['char'] == c:
                find = True
                node = child_dict
                break
        if not find:
            return []
    rec_len = 5
    rec_list = []
    for i in range(rec_len):
        word = get_best_word(node)
        if word is None:
            break
        rec_list += [prefix + word]
    return rec_list


SUMMARY_CHARS = 140

def fill_in_summary(results, keywords):
    t = Thread(target=async_scan_files, args=([item["index"] for item in results],), daemon=True)
    t.start()
    for i, result in enumerate(results):
        doc = result["index"]
        if doc in document_cache:
            full_text = document_cache[doc]["全文"]
        else:
            full_text = parse(get_paper_info(doc)['path']).documentElement.getElementsByTagName("QW")[0].getAttribute("value")
        offsets = []
        for word in keywords:
            if word not in full_text:
                continue
            index = full_text.index(word)
            offset_word = [index]
            while True:
                try:
                    index = full_text.index(word, index + len(word))
                    offset_word.append(index)
                except ValueError as e:
                    break
            offsets.extend(offset_word)
        offsets.sort()
        selection_index, max_word_count = 0, 0
        # slide window start, slide window end
        swe = 0
        for sws in range(len(offsets)):
            while swe < len(offsets) and offsets[swe] - offsets[sws] < SUMMARY_CHARS:
                swe += 1
            if swe - sws > max_word_count:
                max_word_count = swe - sws
                selection_index = sws
        if len(offsets) == 0:
            result["摘要"] = str(keywords)
            continue
        slice_start, slice_end = offsets[selection_index], offsets[selection_index + max_word_count - 1]
        slice_start = max(0, slice_start - max(0, int((SUMMARY_CHARS - (slice_end - slice_start)) / 2)))
        result["摘要"] = ("..." if slice_start > 0 else "") + full_text[slice_start:slice_start+SUMMARY_CHARS] + ("..." if slice_start + SUMMARY_CHARS < len(full_text) else "")

MAX_RECOMMENDATION = 5

def get_single_detail(doc):
    if doc in document_cache:
        return document_cache[doc]
    if doc not in summary_cache:
        get_meta_info([doc])
    root = parse(get_paper_info(doc)['path']).documentElement
    keys = ["title", "LB", "ALYZ", "QW", "WS", "JBFY", "AH", "CPSJ", "DSR", "DSRD", "SSJL", "AJJBQK", "AJJBQKD", "AJSSD", "CPFXGC", "QSFXD", "PJJG", "BSPJJG", "WW", "AJLB", "SPCX", "WSZL", "XZQH_P", "JAND"]
    # 标题，案例类别，全文，文首，经办法院，案号，裁判时间，当事人，当事人段，诉讼记录，案件基本情况，案件基本情况段，案件事实段，裁判分析过程，起诉分析段，判决结果，本审判决结果，文尾，案件类别，审判程序，文书种类，行政区划(省)，结案年度
    # escape_keys = {"AJLB", "SPCX", "WSZL", "XZQH_P", "JAND"}  # 不需要加格式的字段
    item = {}
    item["filename"] = get_paper_info(doc)['path']
    for xml_key in keys:
        elems = root.getElementsByTagName(xml_key)
        if xml_key in key_to_cn and key_to_cn[xml_key] in summary_cache[doc]:
            key_cn = key_to_cn[xml_key]
            item[key_cn] = summary_cache[doc][key_cn]
            continue
        if len(elems) == 0:
            continue
        if elems[0].hasAttribute("nameCN"):
            key_cn = elems[0].getAttribute("nameCN")
        elif xml_key in key_to_cn:
            key_cn = key_to_cn[xml_key]
        else:
            continue
        value = ""
        for elem in elems:
            if elem.hasAttribute("value"):
                value = elem.getAttribute("value")
                break
        if xml_key == "DSRD":
            value = " ".join([x.getAttribute("value") for x in elems])
        item[key_cn] = value
    keys_from_db = ["法官人员完整", "法律法条分组"]
    keys_to_frontend = ["同法官案件推荐", "同法律案件推荐"]
    item = {**item, **{key : summary_cache[doc][key] for key in keys_from_db}, **{_: [] for _ in keys_to_frontend}}
    for i in range(len(keys_from_db)):
        key_name = keys_from_db[i]
        for value in item[key_name]:
            cases = [case for case in query_by_condition({key_name: value}) if case["pid"] != doc]
            if len(cases) > MAX_RECOMMENDATION:
                random.shuffle(cases)
            item[keys_to_frontend[i]].append(cases[:MAX_RECOMMENDATION])
    document_cache[doc] = item
    return item


def get_recommended_doc(text):
    # TODO
    pass


def main_loop():
    while True:
        target = input("Input Search Keyword:")
        target = list(filter(lambda x: re.match(r"[0-9\u4e00-\u9af5]+", x) is not None, [item[0] for item in cutter.cut(target)]))
        doc_recall = recall(target)
        doc_index = rank(doc_recall)
        doc_content = get_meta_info(doc_index)
        for i, content in enumerate(doc_content):
            print("Doc", doc_index[i])
            print(content)
        print("Find {} Items: {} / {}".format(len(doc_recall), doc_recall, doc_index))


if __name__ == "__main__":
    # doc_files, inverted_index = unpack_info(doc_files_store, inverted_index_store)
    main_loop()
