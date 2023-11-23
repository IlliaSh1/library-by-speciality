from django import forms
# from .models import *
from discipline_selection.models import Discipline
from .fields import ListTextWidget
from book_parser.models import Book

from django.db.models import Q
from django.contrib.auth.models import AnonymousUser

class SearchBookGetForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SearchBookGetForm, self).__init__(*args, **kwargs)
        
    
    search_text = forms.CharField(label="Поиск по содержимому", max_length=200,
                                   required=False)
    
    SEARCH_PARAMS_OPTIONS = (
        ("search_in_name", "Искать в названии"),
        ("search_in_annotation", "Искать в описании/аннотации"),
    ) 
    search_params = forms.MultipleChoiceField( 
        label = "Параметры поиска",
        widget = forms.CheckboxSelectMultiple,
        choices = SEARCH_PARAMS_OPTIONS,
        initial = SEARCH_PARAMS_OPTIONS[0][0],
        required = False
    )

    favorite_params = forms.BooleanField(label="Искать в избранных", 
                                        required=False)

    discipline = forms.CharField(
        label="Дисциплина",
        max_length=200, 
        widget=ListTextWidget(data_list=Discipline.objects.all(), name='discipline-list'),
        required=False)
    
    year_published = forms.IntegerField(label="Год публикации", required=False)
    YEAR_PUBLISHED_OPTIONS = (
        ("equal", "В данный год"),
        ("later", "Не раньше"),
        ("sooner", "Не позже"),
    )
    year_published_params = forms.ChoiceField(
        label = "Выпущены",
        widget = forms.RadioSelect(
            attrs={'class': 'Radio'}
        ),
        choices = YEAR_PUBLISHED_OPTIONS,
        initial = YEAR_PUBLISHED_OPTIONS[0][0],
        required=False,
    )
    
    authors = forms.CharField(label="ФИО автора", max_length=200, 
                              required=False)
    
    SORTING_OPTIONS = (
        ("year", "Году"),
        ("name", "Названию"),
    )
    
    
    isbn = forms.CharField(label="ISBN", max_length=12, 
                           required=False,)
    

    sorting = forms.ChoiceField(
        label = "Сортировать по",
        choices = SORTING_OPTIONS,
        required=False
    )
    sorting_params = forms.BooleanField(label="В обратном порядке", 
                                        required=False)
    
    def search(self, user):

        # search text        
        val_search_text = self.cleaned_data['search_text'] or ''
        val_search_params = self.cleaned_data['search_params'] or ''
        
        words_search_pre = val_search_text.replace('.', ' ').replace(',', 
                        ' ').split(' ')
        words_search_list = []
        for word in words_search_pre:
            if(word != ' ' and word != ''):
                words_search_list.append(word)


        query = Q()
        if(len(words_search_list) > 0):
            if(val_search_params != ''):
                if('search_in_name' in val_search_params):
                    subquery = Q()
                    for word in words_search_list:
                        subquery &= Q(name__icontains = word)
                    query |= (subquery)
                if('search_in_annotation' in val_search_params):
                    query |= Q(annotation__icontains = 
                            self.cleaned_data['search_text'])
            else:
                # search standard in book name
                subquery = Q()
                for word in words_search_list:
                    subquery &= Q(name__icontains = word)
                query |= (subquery)
                
        query = (query)
        # 
        val_favorite_params = self.cleaned_data['favorite_params'] or ''
        if(user != AnonymousUser()):
            if(val_favorite_params != ''):
                query &= Q(user = user)
        
        # discipline
        val_discipline = self.cleaned_data['discipline'] or ''
        if(val_discipline != ''):
            query &= Q(disciplines__name = val_discipline)
        
        # author
        val_author = self.cleaned_data['authors'] or ''
        if(val_author != ''):
            query &= Q(authors__fullname__icontains = val_author)

        # isbn
        val_isbn = self.cleaned_data['isbn'] or ''
        if(val_isbn != ''):
            query &= Q(isbn__icontains = val_isbn)
        
        # year
        val_year_published = self.cleaned_data['year_published'] or ''
        val_year_published_params = self.cleaned_data['year_published_params'] or ''
        if(val_year_published != ''):
            if (val_year_published_params == ''):
                query &= Q(year_published = val_year_published)
            else:
                if(val_year_published_params == 'equal'):
                    query &= Q(year_published = val_year_published)
                elif (val_year_published_params == 'later'):
                    query &= Q(year_published__gte = val_year_published)
                elif (val_year_published_params == 'sooner'):
                    query &= Q(year_published__lte = val_year_published) 

        # Sorting
        order_by_query_str = ''

        val_sorting = self.cleaned_data['sorting'] or None
        val_sorting_params = self.cleaned_data['sorting_params'] or None
        
        # Reversing sorting if selected.
        if val_sorting_params:
            order_by_query_str = '-'
        
        sorting_keys = {
            'year': "-year_published",
            'name': "name",
        }
        
        if val_sorting and val_sorting in sorting_keys:
            order_by_query_str += sorting_keys[val_sorting]
        else: 
            order_by_query_str += "-year_published"
            
        print('%s: ordering' % order_by_query_str)

        if order_by_query_str[0:2] == '--':
            order_by_query_str = order_by_query_str[2:]

        print(order_by_query_str[0:1])
        
        return Book.objects.filter(
            query
        ).order_by(order_by_query_str)