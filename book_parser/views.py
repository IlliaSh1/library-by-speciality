from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse


# from django.views import generic

# drf serializing.
from rest_framework import generics, filters
from rest_framework.viewsets import ModelViewSet

from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import BookSerializer, AuthorSerializer

from rest_framework.permissions import AllowAny, IsAuthenticated
## drf filtering.
from django_filters.rest_framework import DjangoFilterBackend
# libraries for async parsing.
import requests, asyncio, aiohttp, httpx
from bs4 import BeautifulSoup
# Models.
from .models import Book, Author
from lib_by_spec.models import Favorite_book

from django.db.models import Q
# Saving parsed images of book covers.
import book_parser
import os.path

import time

# Api for parsed books.
class BookApiView(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny, ]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['year_published']
    search_fields = ['name']
    ordering_fields = ['year_published', 'name']
    
    # Get all books marked as favorite for current user.
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def get_favorite_books(self, request):
        user = request.user
        favorite_books = user.favorite_books.all()
        serializer = BookSerializer(favorite_books, many=True)
        return Response(serializer.data)

    # Add book to favorite for current user.
    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def add_to_favorite(self, request, pk=None):
        try:
            book = self.get_object()
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=404)

        user = request.user
        
        favorite_book, was_created = Favorite_book.objects.get_or_create(
            user=user,
            book=book
        )

        if not was_created:
            favorite_book.delete()
            return Response({"message": f"Book '{book.name}' removed from favorite."}, status=200)
        
        
        return Response({"message": f"Book '{book.name}' added to favorite."}, status=200)

    



class BookListApiView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny, ]
    
    # filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    # search_fields = ['name']
    # ordering_fields = ['year', 'name']
    
    def get_queryset(self):
        # context = super().get_queryset()
        # query = self.request.query_params.get('authors', '')
        year_published = self.request.query_params.get('year', None)
        search_text = self.request.query_params.get('search_text', None)
        if year_published:
            return self.queryset.filter(Q(year_published=year_published))    
        if search_text:
            return self.queryset.filter(Q(name__icontains=search_text) | Q(authors__fullname=search_text))
        return self.queryset.filter()

class BookDetailApiView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny, ]


# Author Api    
class AuthorApiView(ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny, ]



# Classes and functions for parsing books from znanium.com.
def index(request):
    return render(request, "book_parser/index.html", {})

def results(request):
    return render(request, "book_parser/results.html", {})

def processing(request):
    return render(request, "book_parser/processing.html", {})  

def parse_start(request):
    # try:
    #     was_parse_znanium_request = request.POST['znanium']
    # except (KeyError):
    #     return render(request, "book_parser/index.html", {
    #         "error_message": "Incorrect post request",
    #     })
    # else: 
    process = parseZnanium()
    process.start()
    return HttpResponseRedirect(reverse("book_parser:processing", args=()))

class parseZnanium:
    HEADERS = {
        "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }
    BASE_URL = "https://znanium.com"
    SEARCH_URL = "https://znanium.com/catalog/books/udc/004/publications?submitted=1&sub=2&sort=year&per-page=100"
    
    books_data = []
    book_data = {
        # located in outer book page
        'name': None,
        'link': None,
        'img_link': None,
        
        'year_pub': None,
        'pages_count': None,
        'authors': None,

        # not yet added field to Table Book field
        'publisher': None,
        'education_lvl': None,
        'type': None,

        # located in inner book page
        'annotation': None,
        'bibl_record': None,
        'isbn': None,

        # What disciplines belong to
        'disciplines': None,
    }
    pages_not_found = 0
    pages_found = 0

    books_not_found = 0
    books_found = 0

    max_repeat_tries = 2

    max_catalog_pages = 50
    max_book_pages = 5_000

    # max_catalog_pages = 1
    # max_book_pages = 1

    def start(self):
        start_time = time.time()
        print("Начало парсинга znaniuma")
        # Парсинг каталога
        asyncio.run(self.gather_outer_data())
        # Парсинг найденных книг
        asyncio.run(self.gather_inner_data())
        # Добавление книг в БД
        self.save_gathered_books()
        # Скачивание изображений
        self.gather_images_data()
        # Добавление дисциплин к книгам


        cur_time = time.time()
        passed_time = cur_time - start_time
        print("Всего прошло {0:.1f} секунд".format(passed_time))

    def save_gathered_books(self):
        print("Сохраняем книги в базу данных")
        book_i = 0
        for book in self.books_data:
            book_i += 1
            try:

                if(book_i > self.max_book_pages):
                    break
                book_entry, was_created = Book.objects.get_or_create(
                    link = book['link'],
                    name = book['name'],
                )

                pth = os.path.dirname(book_parser.__file__)
                img_str =  "/book_parser/covers/" + str(book_entry.id) + '.jpg'
                
                book_entry.cover = img_str

                book_entry.annotation = book['annotation']
                book_entry.bibl_record = book['bibl_record']
                book_entry.year_published = book['year_pub']
                book_entry.pages_count = book['pages_count']
                book_entry.isbn = book['isbn']
                
                
                book_authors_set = []
                if(book['authors'] != None):
                    for author in book['authors']:
                        author_entry, created = Author.objects.get_or_create(
                            fullname=author
                        )
                        book_entry.authors.add(author_entry)

                self.books_data[book_i - 1]['db_id'] = book_entry.id


                book_entry.save()
                print("Сохранена книга", self.books_data[book_i - 1]['link'])
            except:
                print("Не сохранена", self.books_data[book_i - 1]['link'])
            # print(book)
            # print()
            # print()
            # print(book_authors_set)
            
            # print(book_entry)
            # print(book_entry.id, self.books_data[book_i - 1]['db_id'])
            # print(self.books_data[0]['db_id'])
        print("Книги сохранены")
        

    # downloading images
    def gather_images_data(self):


        books_count = len(self.books_data)
        print("[INFO] Всего обложек:", len(self.books_data))
        print("[INFO] Добавляем задачи обложек...")


        max_task_cnt = self.max_book_pages
        
        for page in range(1, min(books_count + 1, max_task_cnt + 1 )):
            self.get_book_image_data(page - 1)
                # task = asyncio.create_task(self.get_book_image_data(client, page - 1))
                # tasks.append(task)
                # if (page % task_per_gather == 0 or 
                #     page == min(books_count + 1, max_task_cnt + 1) - 1):

                #     print("[INFO] Собираем с", int((page-1)/task_per_gather) * task_per_gather + 1,
                #            "по", page,
                #            "задачи обложек книг")
                #     await asyncio.gather(*tasks)
                #     tasks = []
                # print("[INFO] Задачи обложек собраны")


    # Получение данных со страниц книг
    def get_book_image_data(self, idx):
        url = self.books_data[idx]['img_link']
        # print(idx)
        # print(url, self.books_data[idx]['db_id'])
        # print(self.books_data[idx])
        # i_try = 0
        # while i_try < self.max_repeat_tries:
        #     i_try += 1
        #     # try:
        pth = os.path.dirname(book_parser.__file__)
        img_str = pth + "/static/book_parser/covers/" + str(self.books_data[idx]['db_id']) + '.jpg'
        print(img_str)
        with open(img_str, 'wb') as handle:
            response = requests.get(url, stream=True)

            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)
            # except:
            #     print(f"Ошибка ожидания ответа книги {self.books_data[idx]['img_link']}")   
            # else:
            print(f"Обложка {idx} обработана")

    # Парсинг страниц каталога
    async def get_outer_page_data(self, client, page):
        url = self.SEARCH_URL+f"&page={page}"
        # timeout = httpx.Timeout(10.0, read_timeout=None)
        async with httpx.AsyncClient() as client:
            i_try = 0
            # Массив для сохранения в общий
            books_data = []
            for i_k in range(100):
                books_data.append({
                    # located in outer book page
                    'name': None,
                    'link': None,
                    'img_link': None,
                    
                    'year_pub': None,
                    'pages_count': None,
                    'authors': None,

                    # not yet added field to Table Book field
                    'publisher': None,
                    'education_lvl': None,
                    'type': None,

                    # located in inner book page
                    'annotation': None,
                    'bibl_record': None,
                    'isbn': None,

                    # What disciplines belong to
                    'disciplines': None,
                })
                

            i_book_on_page = 0
            while i_try < self.max_repeat_tries:
                i_try += 1
                try:
                    response = await client.get(url, headers=self.HEADERS, timeout=50.0)
                except:
                    print(f"Ошибка ожидания ответа страницы {page}")       
                else:
                    print(f"Получена страница {page}")
                    soup = BeautifulSoup(response.text, "html.parser")
                    book_list = soup.find_all('div', class_="book-list__item")
                    
                    # Удаление лишних данных
                    soup = None
                    # book_data = {}
                    # Получение данных книг со страницы каталога
                    for book_outer in book_list:
                        # Ссылка
                        try:
                            books_data[i_book_on_page]['link'] = self.BASE_URL + book_outer.find('div', 
                                class_="book-list__img").find('a')['href']
                        except:
                            print("[ERROR] Ссылка книги не найдена")
                            print()
                            # Пропустить если нет ссылки
                            i_book_on_page += 1
                            continue
                        # Название
                        try:
                            books_data[i_book_on_page]['name'] = self.correct_str(
                                book_outer.find('div',
                                    class_="book-list__title").text
                            )
                        except:
                            print("[ERROR] Название не найдено")
                            print(books_data[i_book_on_page]['link'])
                            print()
                            i_book_on_page += 1
                            continue
                        # Ссылка на обложку
                        try:
                            books_data[i_book_on_page]['img_link'] = (
                                self.BASE_URL + self.correct_str(
                                    book_outer.find('div',
                                        class_="book-list__img").find(
                                            'img'
                                        )['src']
                                )
                            )
                        except:
                            print("[ERROR] Обложка не найдена")
                            print(books_data[i_book_on_page]['link'])
                            print('')
                        # Год издания
                        try:
                            books_data[i_book_on_page]['year_pub'] = self.get_book_year_pub(
                                book_outer.find('div', 
                                    class_="qa_booklist_year").text
                            )
                            
                        except:
                            print("[ERROR] Год издания не найден")
                            print(books_data[i_book_on_page]['link'])
                            print()
                        # Количество страниц
                        try:
                            books_data[i_book_on_page]['pages_count'] = self.get_pages_count(
                                book_outer.find('div', 
                                    class_="qa_booklist_year").text
                            )
                        except:
                            print("[ERROR] Количество страниц не найдено")
                            print(books_data[i_book_on_page]['link'])
                            print()
                        # Авторы
                        try:
                            books_data[i_book_on_page]['authors'] = self.get_authors(
                                book_outer.find('div', 
                                    class_="qa_booklist_autors").find_all('a')
                            )
                        except:
                            # print("[ERROR] Авторы не найдены")
                            # Ещё могут быть на странице книги
                            pass
                        # Вид издания
                        try:
                            books_data[i_book_on_page]['type'] = self.correct_str(
                                book_outer.find('div', 
                                    class_="qa_booklist_publication-type").find(
                                        'a').text
                            )
                        except:
                            print("[ERROR] Вид издания не найдено")
                            print(books_data[i_book_on_page]['link'])
                            print()
                        # Уровень образования
                        try:
                            books_data[i_book_on_page]['education_lvl'] = self.correct_str(
                                book_outer.find('div', 
                                    class_="qa_booklist_level-education").find(
                                        'a').text
                            )
                        except:
                            print("[ERROR] Уровень образования не найден")
                            print(books_data[i_book_on_page]['link'])
                            print()
                        # Издательство
                        try:
                            books_data[i_book_on_page]['publisher'] = self.correct_str(
                                book_outer.find('div', 
                                    class_="qa_booklist_publisher").find(
                                        'a').text
                            )
                        except:
                            print("[ERROR] Издательство не найдено")
                            print(books_data[i_book_on_page]['link'])
                            print()




                        # Добавляем книгу в список
                        
                        self.books_data.append(books_data[i_book_on_page])
                        i_book_on_page += 1


                    print(f"[INFO] Обработана страница {page}")
                    break
            if(i_try == self.max_repeat_tries):
                print(f"Страница {page} - Исчерпаны попытки")
                self.pages_not_found += 1
            else:
                self.pages_found += 1
            

    async def gather_outer_data(self):
        url = self.SEARCH_URL

        async with httpx.AsyncClient() as client:
            for i in range(self.max_repeat_tries):
                try:
                    response = await client.get(url=url, headers=self.HEADERS)
                except:
                    print("[Error] Ошибка получения пагинации")
                    if(i == self.max_repeat_tries - 1):
                        return
                else:
                    break
            # print(response.text)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            pages_count = int(soup.find_all('div', 
                                            class_="paging__item")[-1].text)
            
            books_count = self.get_book_count(soup.find('div',
                           class_="catalog-top-panel__meta").text)
            

            # Очищаем лишние данные
            soup = None

            print("[INFO] Найдено страниц:", pages_count)
            print("[INFO] Найдено книг:", books_count)
            tasks = []
            print("[INFO] Добавляем задачи...")

            task_per_gather = 50
            max_task_cnt = self.max_catalog_pages
            for page in range(1, min(pages_count + 1, max_task_cnt + 1)):
                task = asyncio.create_task(self.get_outer_page_data(client, page))
                tasks.append(task)
                if (page % task_per_gather == 0 or 
                    page == min(pages_count + 1, max_task_cnt + 1) - 1):

                    print("[INFO] Собираем с", int((page-1)/task_per_gather) * task_per_gather + 1,
                           "по", page,
                           "задачу")
                    time.sleep(1)
                    await asyncio.gather(*tasks)
                    tasks = []
                    print("[INFO] Задачи собраны - страницы каталога обработаны")
            print("[END INFO] Все страницы каталога обработаны!")
        
            
    # Получение данных со страниц книг
    async def get_inner_page_data(self, client, idx):
        url = self.books_data[idx]['link']
        
        async with httpx.AsyncClient() as client:
            i_try = 0
            while i_try < self.max_repeat_tries:
                i_try += 1
                try:
                    response = await client.get(url, headers=self.HEADERS, 
                                                timeout=50.0)
                except:
                    print(f"Ошибка ожидания ответа книги {self.books_data[idx]['link']}")       
                else:
                    # print(f"Получена книга {self.books_data[idx]['link']}")
                    soup = BeautifulSoup(response.text, "html.parser")
                    book_inner = soup.find('div', class_="catalog")
                    
                    # Удаление лишних данных
                    soup = None
                    # Получение данных книги из её страницы
                    
                    # Авторы, если не были найдены в каталоге
                    if self.books_data[idx]['authors'] == None:
                        try:
                            self.books_data[idx]['authors'] = self.inner_get_authors(
                                book_inner.find_all('div', 
                                    class_="qa_booklist_autors")
                            )
                            # print("[INFO] Авторы внутри найдены")
                        except:
                            print("[ERROR] Авторы внутри не найдены")
                            print(self.books_data[idx]['link'])
                            print()
                    
                    # Isbn
                    try:
                        self.books_data[idx]['isbn'] = self.correct_str(
                            book_inner.find('div', 
                                class_="qa_booklist_isbn").text
                        )
                    except:
                        # print("[ERROR] Isbn не найден")
                        # print(self.books_data[idx]['link'])
                        # print()
                        pass
                    # Аннотация
                    try:
                        self.books_data[idx]['annotation'] = self.correct_str(
                            book_inner.find('div', {"nav": "ant"}).text
                        )
                    except:
                        # print("[ERROR] Аннотация не найдена")
                        # print(self.books_data[idx]['link'])
                        # print()
                        pass
                    # Бибзапись
                    try:
                        self.books_data[idx]['bibl_record'] = self.correct_str(
                            book_inner.find('pan', {"id": "doc-biblio-card"}).text
                        )
                    except:
                        print("[ERROR] Бибзапись не найдена")
                        print(self.books_data[idx]['link'])
                        print()

                    
                    # print(f"[INFO] Обработана книга {self.books_data[idx]['link']}")
                    break
            if(i_try == self.max_repeat_tries):
                print(f"Книга {self.books_data[idx]['link']} - Исчерпаны попытки")
                self.books_not_found += 1
            else:
                self.books_found += 1


    async def gather_inner_data(self):
        print()
        print("[START INFO] Собираем страницы найденных книг")
        if len(self.books_data) > 1:
            print(len(self.books_data), '1 book == 2 book is ', self.books_data[0] == self.books_data[1] )
        async with httpx.AsyncClient() as client:
            books_count = len(self.books_data)
            print("[INFO] Всего страниц книг:", len(self.books_data))
            tasks = []
            print("[INFO] Добавляем задачи книг...")

            task_per_gather = 50
            max_task_cnt = self.max_book_pages
            
            for page in range(1, min(books_count + 1, max_task_cnt + 1 )):
                task = asyncio.create_task(self.get_inner_page_data(client, page - 1))
                tasks.append(task)
                if (page % task_per_gather == 0 or 
                    page == min(books_count + 1, max_task_cnt + 1) - 1):

                    print("[INFO] Собираем с", int((page-1)/task_per_gather) * task_per_gather + 1,
                           "по", page,
                           "задачи книг")
                    await asyncio.gather(*tasks)
                    tasks = []
                    print("[INFO] Задачи книг собраны")
            print("[INFO] Все страницы книг обработаны!")
    

    
            

    # Обработка данных тэгов и др.
    def get_book_count(self, book_count_text):
        book_count = ''
        book_count_text = self.correct_str(book_count_text)
        for i in book_count_text:
            if(i >= '0' and i <='9'):
                book_count += i
            if i == ',':
                break

        book_count = int(book_count) 
        return book_count
    
    def get_book_year_pub(self, book_year_pub_text):
        book_year_pub_text = self.correct_str(book_year_pub_text)
        year_pub_pref_text = "Год издания:"
        book_year_pub = ''
        flag_f = False
        i=0
        while(i < len(book_year_pub_text)):
            i_sim = book_year_pub_text[i]
            if not flag_f:
                i_cur = i
                for j in year_pub_pref_text:
                    if j != book_year_pub_text[i_cur]:
                        break

                    if(j == ':'):
                        flag_f = True
                        i = i_cur + 1
                        break
                    i_cur += 1
            else:
                if(i_sim >= '0' and i_sim <= '9'):
                    book_year_pub+=i_sim
                elif i_sim != ' ' or i_sim !='\n':
                    break
            i+=1
        book_year_pub = int(book_year_pub)
        return book_year_pub
    
    def get_pages_count(self, book_pages_count_text):
        book_pages_count_text = self.correct_str(book_pages_count_text)
        pages_count_pref_text = "Кол-во страниц:"
        book_year_pub = ''
        flag_f = False
        i=0
        while(i < len(book_pages_count_text)):
            i_sim = book_pages_count_text[i]
            if not flag_f:
                i_cur = i
                for j in pages_count_pref_text:
                    if j != book_pages_count_text[i_cur]:
                        break

                    if(j == ':'):
                        flag_f = True
                        i = i_cur + 1
                        break
                    i_cur += 1
            else:
                if(i_sim >= '0' and i_sim <= '9'):
                    book_year_pub+=i_sim
                elif i_sim != ' ' or i_sim !='\n':
                    break
            i+=1
        book_year_pub = int(book_year_pub)
        return book_year_pub
    
    def get_authors(self, book_authors_text):
        book_authors = []
        for author in book_authors_text:
            book_authors.append(self.correct_str(author.text))
        return book_authors
    
    def inner_get_authors(self, authors_containers):
        book_authors = []

        for authors_container in authors_containers:
            for author in authors_container.find_all('a'):
                book_authors.append(self.correct_str(author.text))
        return book_authors
    
    # Вспомогательные функции
    def correct_str(self, s):
        res = ""
        sz = len(s)
        # Вернуть пустую строку
        if sz == 0:
            return res
        i = 0
        # Убрать начальные пробелы и переносы
        while s[i] == ' ' or s[i] == '\n':
            i += 1
            if i == sz:
                i -= 1
                break
        l = i
        i = len(s) - 1
        # Убрать конечные пробелы и переносы
        while s[i] == ' ' or s[i] == '\n':
            i -= 1
            if i == -1:
                i += 1
                break
        r = i
        res += s[l]
        for i in range(l + 1, r + 1):
            # Не добавляем последовательные пробелы/переносы
            if s[i] == ' ' or s[i] == '\n':
                continue
            # Исключаем лишние пробелы перед ',' '.' ':'
            if(s[i] != '.' and s[i] != ',' and s[i] != ':'):
                if  s[i - 1] == ' ' or s[i - 1] == '\n':
                    res += s[i-1]
            res += s[i]
        if res == '\n' or res == ' ':
            res = ""
        return res
    
if __name__ == "__main__":
    parse_start("a")


    
