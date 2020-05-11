from django.http import HttpResponse
from SearchEngine.models import *


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
