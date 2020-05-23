from django.http import HttpResponse
from SearchEngine.models import *
import pickle, json
from .search import *

doc_files_store = "../../temp/filename.pkl"
inverted_index_store = "../../temp/inverted_index.json"
doc_files, inverted_index = unpack_info(doc_files_store, inverted_index_store)
doc_files = ["../../" + file for file in doc_files]

def response(body):
    responses = HttpResponse(body)
    responses["Access-Control-Allow-Origin"] = "*"
    responses['Access-Control-Allow-Headers'] = "content-type"
    return responses

def test(request):
    for x in InvertedIndex.objects[:10]:
        print(x.term, x.appear)
    return HttpResponse('success')


def query(request):
    ''' query for a single word '''
    term = request.GET.get('term')
    inverted_index = InvertedIndex.objects(term=term)
    print(len(inverted_index))
    res = ''
    if len(inverted_index) > 0:
        appear_list = inverted_index[0].appear
        for appear in appear_list:
            res += '<h3>' + str(appear.paper_id) + ' ' + str(appear.offset) + '</h3>'
    return HttpResponse(res)

def search(request):
    query = request.GET.get('searchkey')
    condition = {key: request.GET.get(key) for key in need_stats_keys if request.GET.get(key) is not None}
    query_words = list(filter(lambda x: re.match(r"[0-9\u4e00-\u9af5]+", x) is not None, [item[0] for item in cutter.cut(query)]))
    query_words = list(set(query_words))
    doc_recall = recall(query_words, inverted_index)
    print(condition)
    doc_recall = filters(doc_recall, condition, doc_files)
    doc_rank = rank(doc_recall, query_words, inverted_index)
    doc_content = get_summary(doc_rank, doc_files)
    return response(json.dumps(doc_content, ensure_ascii=False))

def detail(request):
    index = int(request.GET.get('index'))
    doc_content = get_single_detail(index, doc_files)
    return response(json.dumps(doc_content, ensure_ascii=False))