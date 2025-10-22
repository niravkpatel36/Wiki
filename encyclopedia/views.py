from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.http import HttpResponseRedirect
import random
import markdown2

from . import util

class SearchForm(forms.Form):
    q = forms.CharField(label="", widget=forms.TextInput(attrs={
        "placeholder": "Search Encyclopedia"
    }))

class PageForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100)
    content = forms.CharField(label="Content (Markdown)", widget=forms.Textarea)

def index(request):
    entries = util.list_entries()
    search_form = SearchForm()
    return render(request, "encyclopedia/index.html", {
        "entries": entries,
        "search_form": search_form
    })

def entry_view(request, title):
    """
    Show a wiki entry. If not found -> render error page.
    Convert Markdown to HTML using markdown2.
    """
    entry_md = util.get_entry(title)
    search_form = SearchForm()
    if entry_md is None:
        return render(request, "encyclopedia/notfound.html", {
            "title": title,
            "search_form": search_form
        })
    entry_html = markdown2.markdown(entry_md)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": entry_html,
        "search_form": search_form
    })

def search(request):
    """
    Handle search form. If exact match -> redirect to entry.
    Otherwise show list of substring matches (case-insensitive).
    """
    if request.method == "GET":
        query = request.GET.get("q", "").strip()
    else:
        query = request.POST.get("q", "").strip()

    if not query:
        return redirect("encyclopedia:index")

    entries = util.list_entries()
    for e in entries:
        if e.lower() == query.lower():
            return redirect("encyclopedia:entry", title=e)

    results = [e for e in entries if query.lower() in e.lower()]

    search_form = SearchForm(initial={"q": query})
    return render(request, "encyclopedia/search.html", {
        "query": query,
        "results": results,
        "search_form": search_form
    })

def new_page(request):
    """
    Create a new page. If POST and title exists -> error page.
    Otherwise save and redirect to the new entry.
    """
    if request.method == "POST":
        form = PageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"].strip()
            content = form.cleaned_data["content"]
            entries = util.list_entries()
            if any(e.lower() == title.lower() for e in entries):
                search_form = SearchForm()
                return render(request, "encyclopedia/create_error.html", {
                    "title": title,
                    "search_form": search_form
                })
            util.save_entry(title, content)
            return redirect("encyclopedia:entry", title=title)
    else:
        form = PageForm()
    search_form = SearchForm()
    return render(request, "encyclopedia/new.html", {
        "form": form,
        "search_form": search_form
    })

def edit_page(request, title):
    """
    Edit an existing page: pre-populate textarea with current markdown.
    Save updated markdown and redirect back to entry view.
    """
    entry_md = util.get_entry(title)
    if entry_md is None:
        search_form = SearchForm()
        return render(request, "encyclopedia/notfound.html", {
            "title": title,
            "search_form": search_form
        })

    if request.method == "POST":
        content = request.POST.get("content", "")
        util.save_entry(title, content)
        return redirect("encyclopedia:entry", title=title)
    else:
        form = PageForm(initial={"title": title, "content": entry_md})
        search_form = SearchForm()
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "form": form,
            "search_form": search_form
        })

def random_page(request):
    entries = util.list_entries()
    if not entries:
        return redirect("encyclopedia:index")
    title = random.choice(entries)
    return redirect("encyclopedia:entry", title=title)