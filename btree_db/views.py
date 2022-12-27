from django.shortcuts import render

from .src.BTreeDB import BTreeDB


def index(request):
    btree = BTreeDB('db', 1024, truncate=True)
    with btree.open('w'):
        btree[1] = 'abc'
    with btree.open('r'):
        context = {'text': btree[1]}
    return render(request, 'btree_db/index.html', context)
