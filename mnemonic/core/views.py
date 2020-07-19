from django.shortcuts import render

from mnemonic.news.utils.search_utils import get_search_results, get_client


def home(request):
    ctx = {
        'num_docs': get_client().count()
    }
    q = request.GET.get('q')
    if q:
        ctx['q'] = q
        ctx['num_results'], ctx['results'] = get_search_results(q)
    return render(request, 'base.html', ctx)
