from typing import Any, Dict
from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, JsonResponse
from django.views import generic, View
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib import auth


from book_parser.models import Book, Author, Discipline
from .models import Favorite_book
from .forms import SearchBookGetForm

from django.contrib.auth.models import AnonymousUser

import json
import time


class IndexView(generic.ListView):
    template_name = "lib_by_spec/index.html"
    context_object_name = "book_list"
    
    books_per_page = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        
        context['search_book_form'] = self.search_form
        
        get_params = ''

        for key_get in self.request.GET:
            print(key_get)
            for param in self.request.GET.getlist(key_get):
                get_params += key_get+'='+param+'&'

        context['get_params'] = get_params


        # pages
        context['cur_page'] = self.page_num
        context['next_page'] = context['cur_page'] + 1
        context['prev_page'] = context['cur_page'] - 1

        context['cnt_per_page'] = self.page_num

        context['last_page'] = self.last_page

        # prev & next pages
        context['prev_pages'] = []
        context['next_pages'] = []
        page_range = 2


        for i in range(max(self.page_num - page_range, 1), self.page_num): 
            context['prev_pages'].append(i)
        for i in range(self.page_num + 1, min(self.page_num + 1 + page_range,
                                               self.last_page + 1)): 
            context['next_pages'].append(i)

        return context
    


    def get_queryset(self):
        self.cnt_per_page = 1
        self.page_num = 1
        if "page_num" in self.request.GET:
                self.page_num = max(int(self.request.GET['page_num']), 1)



        flag_searched = False
        if(self.request.method == "GET"):
            self.search_form = SearchBookGetForm(
                self.request.GET
            )
                # data_list = Discipline.objects.all(),
            print('check form')
            if(self.search_form.is_valid()):
                print("valid")
                flag_searched = True
                books_filtered = self.search_form.search(auth.get_user(self.request))
            
            else:
                print("form is not valid!")
        
        
            
        # if(books_filtered.all().count() != 0)
        if not flag_searched:
            books_filtered = Book.objects.filter().order_by("-year_published")
            # [:self.books_per_page] 
        
        self.books_paginated = Paginator(books_filtered, self.books_per_page)
        self.last_page = self.books_paginated.num_pages
        print()
        print()
        self.page_num = min(self.page_num, self.last_page)
        print(self.last_page, self.page_num)
        
        self.cur_books = self.books_paginated.page(self.page_num)
        return self.cur_books
    

# Book detail page.
class DetailView(generic.DetailView):
    model = Book
    template_name = "lib_by_spec/detail.html"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['example_cover_link'] = '/book_parser/covers/1553.jpg'
        return context



# Adding book to favorite.
def ToFavorite(request, pk):
    if request.method == 'POST':
        print(json.loads(request.body)['text'])

    response_data = {}

    user = auth.get_user(request)
    
    if user == AnonymousUser():
        print("You are anonymous")
        response_data["success"] = False
        response_data["err_msg"] = 'Для добавления в избранное необходимо войти в аккаунт.'
        return JsonResponse(response_data)
    
    req_book = Book.objects.filter(pk=pk)[0]
    book, was_created = Favorite_book.objects.get_or_create(
        user=user,
        book=req_book
    )
    
    if not was_created:
        book.delete()
    response_data['success'] = True
    response_data['added'] = was_created
    response_data['count'] = Favorite_book.objects.filter(book=req_book).count()
    print(response_data)
    return JsonResponse(response_data)
        





