from django.shortcuts import render_to_response
from django.template import RequestContext
from lexis.models import Word, WordNode, MeanWord
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def home(request):
    return render_to_response('home.html',
                       locals(),
                       context_instance=RequestContext(request))

def search(request):
    keywords = request.POST['keywords']
    print keywords.encode('utf-8')
    words = keywords.split(' ')
    if len(words) < 4:
        word_plain = '_'.join(words)
        mean_words = MeanWord.objects.filter(word__plain__contains=word_plain)
    return render_to_response('home.html',
                       locals(),
                       context_instance=RequestContext(request))

def get_words(request):
    pass

def get_phrases(request, mean_word_id):
    print mean_word_id
    word_nodes = WordNode.objects.filter(word_id=mean_word_id)
    print word_nodes
    phrase_roots = [node.get_parent() for node in word_nodes]
    phrases = []
    for phrase in phrase_roots:
        nodes = []
        for child in phrase.get_children():
            nodes.append(child)
        phrases.append((nodes, phrase))
    return render_to_response('home.html',
                       locals(),
                       context_instance=RequestContext(request))

def get_phrases_by_category(request, cat_code):
    print cat_code
    word_nodes = WordNode.objects.filter(plain=cat_code)

    if cat_code.find('phrase') > 0:
        phrase_roots = word_nodes
    else:
        phrase_roots = [node.get_parent() for node in word_nodes]

    phrase_list = []
    for phrase in phrase_roots:
        nodes = []
        for child in phrase.get_children():
            nodes.append(child)
        phrase_list.append((nodes, phrase))

    paginator = Paginator(phrase_list, 100)

    page = request.GET.get('page')
    try:
        phrases = paginator.page(page)
    except PageNotAnInteger:
        phrases = paginator.page(1)
    except EmptyPage:
        phrases = paginator.page(paginator.num_pages)

    return render_to_response('home.html',
                       locals(),
                       context_instance=RequestContext(request))
