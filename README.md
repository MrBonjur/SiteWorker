# SiteWorker.py - very easy usages!
## Простая библиотека для работы с типовыми сайтами школ


Этот код написан исключительно для образовательных целей. 
Автор не призывает автоматизировать работу на сайте. 
Возможна блокировка по айпи при использовании скрипта не из региона школы.

## Зависимости
Тестировал на Python 3.9
- ```pip install BeautifulSoup4```
- ```pip install requests```
- ```pip install Pillow```




## Настройка config.py

Очень простой конфиг в котором нужно заполнить логи и пароль от сайта.
`is_resize_preview` означает, будет ли скрипт подгонять неподходящие изображения под размер превью.  
####  config.py
```
login = ""
password = ""
is_resize_preview = True
```


## Пример

Посмотреть пример кода можно в [example.py](https://github.com/MrBonjur/SiteWorker/blob/main/example.py)

#### Авторизация и проверка на правильность ввода логина и пароля.
```py
site = SiteWorker.Site(url="https://lyc****.mskobr.ru")
is_logged = site.authorization(login=config.login, password=config.password)

if not is_logged:
    print("Неверный логин или пароль!")
    exit()
```
#### Добавление фотографий в новость
>Чтобы в новости были фотографии, их нужно обработать и преобразовать в html элемент. 
>Слава богу это делается двумя строками :)
```py
image_base64 = SiteWorker.to_base64("test.png")
site_image = SiteWorker.site_photo(image_base64)
```
### Наполнение контентом 

>При минимальных знаниях HTML можно оформлять новость по своему вкусу.
>Самый простой пример текста
```py
content_news = f'<p>Всем привет, это контент в новой записи!</p>'
```
>Добавляем жирный текст и два переноса строки
```py
content_news = f'<p>Всем <b>привет</b>, это контент в новой записи!<br><br></p>'
```
>Добавляем  два одинаковых элемента (фотографии)
```py
content_news = f'<p>Всем <b>привет</b>, это контент в новой записи!<br><br>{site_image}{site_image}</p>'
```
### Публикация новости
>Доступные аругменты:
> * date - Время в формате 2023-01-01 08:00:00
> * news_name - Название новости
> * tags - Строковое число от 0 до 6. (В случае когда 6 тегов на сайте)
> * announcement - Текста анонса
> * preview_path - Путь до файла, которое будет на превью.
> * content - Текст самой новости. (HTML оформление)

Проверяем опубликовалась ли новость. В случае публикации будет статус ответа 406 и будет возращено True.
```py
news = site.send_news(news_name="Hello",
                      date="2023-02-25 08:00:00",
                      preview_path="test.png",
                      content=content_news)
if news:
    print("Новость опубликована!")
```


## Выгрузка любого файла на сайт (pdf, png, jpg, docx...)
> Файл можно выгрузить получив путь до папки на сайте.

![изображение](https://user-images.githubusercontent.com/55990897/220732823-d9af57d3-6a09-4f2e-b4d5-b819c2254ef8.png)


> * path_or_bytes - Можно указать как путь до файла, так и сразу байты файла.
> * title - Название файла.
> * site_path - Это можно получить через код элемента.
```py
file_uploaded = site.upload_file(path_or_bytes="test.png",
                                 title="New File",
                                 site_path="/data/form/file/30130/343/new")
if file_uploaded:
    print("Файл успешно загружен!")
```


## Получение всех файлов
> С любой страницы сайта можно получить всю информацию о файлах.
> Это нужно чтобы удалять по айди.
```py
files = site.parsing_files("/roditelyam/vse-voprosi-o-pitanii")
for file in files:
    print(file)
```
> Этот код выведе следующие строки:

```
{'file_id': '6391', 'path': '/attach_files/upload_users_files/1.pdf', 'file_name': 'Питьевой режим', 'site_path': '/data/form/file/30130/false/6391'}
{'file_id': '6388', 'path': '/attach_files/upload_users_files/2.pdf', 'file_name': 'Меню 1', 'site_path': '/data/form/file/30130/false/6388'}
{'file_id': '6394', 'path': '/attach_files/upload_users_files/3.pdf', 'file_name': 'Меню 2', 'site_path': '/data/form/file/30130/false/6394'}
```

## Удаление файлов
> Берем айди файла из предыдущего пункта, и удаляем файл. 
```py
file_deleted = site.delete_file(file_id="6391")

if file_deleted:
    print("Файл успешно удален!")
```

> ###### Связаться со мной можно в телеграмме [@mrbonjur](https://t.me/mrbonjur)
