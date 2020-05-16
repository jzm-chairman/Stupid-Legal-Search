from django.http import HttpResponse
from SearchEngine.models import *
import pickle, json
from .search import unpack_info, recall, rank, get_content, get_single_detail

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
    doc_counter = recall(query, inverted_index)
    doc_index = rank(doc_counter)
    doc_content = get_content(doc_index, doc_files)
    return response(json.dumps(doc_content, ensure_ascii=False))

def detail(request):
    index = int(request.GET.get('index'))
    doc_content = get_single_detail(index, doc_files)
    return response(json.dumps(doc_content, ensure_ascii=False))