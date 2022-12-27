from django.shortcuts import render, redirect
from .forms import InsertForm, UpdateForm, DeleteForm, ReadForm
from .db import db_operations


def index(request):
    context = {'form': ''}
    return render(request, 'btree_db/index.html', context)


def insert(request):
    if request.method == 'POST':
        form = InsertForm(data=request.POST)
        if form.is_valid():
            db_operations.insert_or_update(form.data)
            return redirect('btree_db:inserted')
    else:
        form = InsertForm()

    context = {'form': form}
    return render(request, 'btree_db/insert.html', context)


def inserted(request):
    return render(request, 'btree_db/inserted.html')


def update(request):
    if request.method == 'POST':
        form = UpdateForm(data=request.POST)
        if form.is_valid():
            db_operations.insert_or_update(form.data)
            return redirect('btree_db:updated')
    else:
        form = UpdateForm()

    context = {'form': form}
    return render(request, 'btree_db/update.html', context)


def updated(request):
    return render(request, 'btree_db/updated.html')


def delete(request):
    if request.method == 'POST':
        form = DeleteForm(data=request.POST)
        if form.is_valid():
            db_operations.delete(form.data)
            return redirect('btree_db:deleted')
    else:
        form = DeleteForm()

    context = {'form': form}
    return render(request, 'btree_db/delete.html', context)


def deleted(request):
    return render(request, 'btree_db/deleted.html')


def delete_all(request):
    db_operations.delete_all()
    return render(request, 'btree_db/deleted_all.html')


def read(request):
    if request.method == 'POST':
        form = ReadForm(data=request.POST)
        if form.is_valid():
            return redirect('btree_db:view', key=form.data['key'])
    else:
        form = ReadForm()

    context = {'form': form}
    return render(request, 'btree_db/read.html', context)


def view(request, key):
    value = db_operations.read({'key': key})
    context = {'value': value, 'key': key}
    return render(request, 'btree_db/view.html', context)


def view_all(request):
    data = db_operations.read_all()
    context = {'data': data}
    return render(request, 'btree_db/view_all.html', context)
