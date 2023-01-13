from django.shortcuts import render, redirect
from .forms import InsertForm, UpdateForm, DeleteForm, ReadForm
from btree_db import db_operations


def index(request):
    context = {'form': ''}
    return render(request, 'btree_app/index.html', context)


def insert(request):
    if request.method == 'POST':
        form = InsertForm(data=request.POST)
        if form.is_valid():
            db_operations.insert_or_update(form.data)
            return redirect('btree_app:inserted')
    else:
        form = InsertForm()

    context = {'form': form}
    return render(request, 'btree_app/insert.html', context)


def inserted(request):
    return render(request, 'btree_app/inserted.html')


def update(request):
    if request.method == 'POST':
        form = UpdateForm(data=request.POST)
        if form.is_valid():
            db_operations.insert_or_update(form.data)
            return redirect('btree_app:updated')
    else:
        form = UpdateForm()

    context = {'form': form}
    return render(request, 'btree_app/update.html', context)


def updated(request):
    return render(request, 'btree_app/updated.html')


def delete(request):
    if request.method == 'POST':
        form = DeleteForm(data=request.POST)
        if form.is_valid():
            db_operations.delete(form.data)
            return redirect('btree_app:deleted')
    else:
        form = DeleteForm()

    context = {'form': form}
    return render(request, 'btree_app/delete.html', context)


def deleted(request):
    return render(request, 'btree_app/deleted.html')


def delete_all(request):
    db_operations.delete_all()
    return render(request, 'btree_app/deleted_all.html')


def read(request):
    if request.method == 'POST':
        form = ReadForm(data=request.POST)
        if form.is_valid():
            return redirect('btree_app:view', key=form.data['key'])
    else:
        form = ReadForm()

    context = {'form': form}
    return render(request, 'btree_app/read.html', context)


def view(request, key):
    value = db_operations.read({'key': key})
    context = {'value': value, 'key': key}
    return render(request, 'btree_app/view.html', context)


def view_all(request):
    data = db_operations.read_all()
    context = {'data': data}
    return render(request, 'btree_app/view_all.html', context)
