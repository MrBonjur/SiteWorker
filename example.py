import SiteWorker
import config

site = SiteWorker.Site(url="https://lyc****.mskobr.ru")
is_logged = site.authorization(login=config.login, password=config.password)

if not is_logged:
    print("Неверный логин или пароль!")
    exit()

# Upload NEWS
image_base64 = SiteWorker.to_base64("test.png")
site_image = SiteWorker.site_photo(image_base64)
# I added 2 images
content_news = f'<p>Всем <b>привет</b>, это контент в новой записи!<br><br>{site_image}{site_image}</p>'
news = site.send_news(news_name="Hello",
                      date="2023-02-25 08:00:00",
                      preview_path="test.png",
                      content=content_news)
if news:
    print("Новость опубликована!")


# Upload FILE
file_uploaded = site.upload_file(path_or_bytes="test.png",
                                 title="New File",
                                 site_path="/data/form/file/30130/343/new")
if file_uploaded:
    print("Файл успешно загружен!")


# Delete FILE

# <li id="8071" class="pdf ui-sortable-handle">
file_deleted = site.delete_file(file_id="8071")

if file_deleted:
    print("Файл успешно удален!")


# Get all files from page
files = site.parsing_files("/roditelyam/vse-voprosi-o-pitanii")
for file in files:
    print(file)


