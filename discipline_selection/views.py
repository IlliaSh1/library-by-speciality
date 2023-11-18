from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from django.views import generic

from django.db.models import Q

from book_parser.models import Book
from .models import Discipline, Keyword


def index(request):
    return render(request, "discipline_selection/index.html", {})

def results(request):
    return render(request, "discipline_selection/results.html", {})

def select(request):

    select_disciplines_for_books()
    return(HttpResponse('ok'))

def select_disciplines_for_books():
    discipline_list = Discipline.objects.all()
    keywords = []
    for idx in range(discipline_list.count()):
        cur_keywords = discipline_list[idx].keywords
        keywords.append(cur_keywords)
    book_list =  Book.objects.all()
    # for book in book_list:
    book_disciplines = []
    book = book_list[0]
    for b_i in range(book_list.count()):
        if(b_i > 0):
            return
        selected_d = [] 
        
        for d_i in range(discipline_list.count()):
            for k in keywords[d_i].all(): 
                query = Q()
                k_words = k.key_phrase.replace('.', ' ').replace(',', 
                        ' ').replace('-', ' ').split(' ')
                print(k.key_phrase)
                
                # subquery_name = Q(name__icontains = k.key_phrase)
                # subquery_annotation = Q(annotation__icontains = k.key_phrase)
                
                subquery_name = Q()
                subquery_annotation = Q()                
                
                # print(k_words)
                for k_word in k_words:
                    if(k_word != ' ' and k_word != ''):
                        subquery_name &= Q(name__icontains = k_word)
                        subquery_annotation &= Q(annotation__icontains = k_word)
                
                query = (subquery_annotation) | (subquery_name)

                filtered_books = Book.objects.filter(query) 
            
                for b in filtered_books:
                    b.disciplines.add(discipline_list[d_i])
                            

        book_disciplines.append(selected_d)

    print(f"[RESULT] {book_disciplines}")

