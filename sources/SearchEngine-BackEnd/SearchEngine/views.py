from django.http import HttpResponse
from SearchEngine.models import *
import pickle, json, time
from .search import *

# doc_files_store = "../../temp/filename.pkl"
# inverted_index_store = "../../temp/inverted_index.json"
# doc_files, inverted_index = unpack_info(doc_files_store, inverted_index_store)
# doc_files = ["../../" + file for file in doc_files]

def response(body):
    responses = HttpResponse(body)
    responses["Access-Control-Allow-Origin"] = "*"
    responses['Access-Control-Allow-Headers'] = "content-type"
    return responses


def search(request):
    print('Enter Search')
    start = time.time()
    query = request.GET.get("searchkey")
    condition = {key: request.GET.get(key) for key in need_stats_keys if request.GET.get(key) is not None}
    query_words = list(filter(lambda x: re.match(r"[0-9\u4e00-\u9af5]+", x) is not None, [item[0] for item in cutter.cut(query)]))
    query_words = list(set(query_words))
    print("Preprocess Time: {}s".format(time.time() - start))
    start = time.time()
    doc_recall = recall(query_words)
    print("Recall Time: {}s".format(time.time() - start))
    print(condition, query_words)
    start = time.time()
    doc_filter = filters(doc_recall, condition)
    print("Filter Time: {}s".format(time.time() - start))
    print("Recall & Filter Size:", len(doc_filter))
    start = time.time()
    doc_rank = rank(doc_filter, query_words)
    print("Rank Time: {}s".format(time.time() - start))
    # print(doc_rank)
    start = time.time()
    page_index, page_size = int(request.GET.get("pageindex")) - 1, int(request.GET.get("pagesize"))
    # doc_page = doc_rank[page_index*page_size:(page_index+1)*page_size]
    # doc_page = doc_rank
    # print(doc_page)
    doc_content = get_summary(doc_rank)
    doc_content["total"] = len(doc_rank)
    doc_content["results"] = doc_content["results"][page_index*page_size:(page_index+1)*page_size]
    print("Summarize Time: {}s".format(time.time() - start))
    print("Page Size = {}, Page Index = {}".format(page_size, page_index))
    print("Summary Cache Size = {}, Document Cache Size = {}".format(len(summary_cache), len(document_cache)))
    return response(json.dumps(doc_content, ensure_ascii=False))


def detail(request):
    index = int(request.GET.get("index"))
    keywords = request.GET.get("searchkey")
    if keywords is not None:
        keywords = set(filter(lambda x: re.match(r"[0-9\u4e00-\u9af5]+", x) is not None, [item[0] for item in cutter.cut(keywords)]))
    else:
        keywords = []
    doc_content = get_single_detail(index, keywords)
    doc_content["searchcut"] = list(keywords)
    return response(json.dumps(doc_content, ensure_ascii=False))