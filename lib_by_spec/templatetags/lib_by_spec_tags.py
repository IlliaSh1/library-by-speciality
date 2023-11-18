from django import template

register = template.Library() 

from django.contrib.auth.models import AnonymousUser

@register.filter(name='has_book_in_favorites') 
def has_book_in_favorites(user, book_id):
    # print
    if(user != AnonymousUser()):
        return user.favorite_books.filter(pk = book_id).exists() 