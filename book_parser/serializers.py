from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from .models import Book, Author
## drf validation.
from rest_framework.validators import UniqueValidator
class StandardPagination(PageNumberPagination):
    page_size = 10

class BookSerializer(serializers.ModelSerializer):
    # authors = serializers.PrimaryKeyRelatedField(
    #     queryset=Author.objects.all(), many=True)
    link = serializers.CharField(
        validators=[
            UniqueValidator(queryset=Book.objects.all(), message="Link must be unique")
        ]
    )
        
    authors = serializers.SerializerMethodField('get_authors_names')
    
    def get_authors_names(self, objects):
        names = []
        authors = objects.authors.get_queryset()
        for author in authors:
            names.append(author.fullname)
        return names
    
    pagination_class = StandardPagination
    
    class Meta:
        model = Book
        fields= '__all__'
        # depth = 1

    # Link validation.    
    def validate_link(self, value):

        if not value.startswith('http'):
            raise serializers.ValidationError("Link must starts with 'http'")
        return value

        
class AuthorSerializer(serializers.Serializer):
    class Meta:
        model = Author
        fields = '__all__'
        
