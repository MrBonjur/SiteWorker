from __future__ import annotations

import base64
import time

import bs4
import requests
from PIL import Image
from bs4 import BeautifulSoup

import config


def to_bytes(data: str | bytes):
    if not data:
        return
    if isinstance(data, bytes):
        return data
    else:
        return open(data, "rb")


def to_base64(path: str):
    with open(path, "rb") as binary_file:
        binary_file_data = binary_file.read()
        base64_encoded_data = base64.b64encode(binary_file_data)
        return "data:image/png;base64," + base64_encoded_data.decode('utf-8')


def site_photo(base64_string: str) -> str:
    # base64 to html element
    return f'<img alt="" src="{base64_string}" style="width: 100%;"/><br><br>'


def resize_for_preview(path):
    # original size preview 200x135, 2mb max file size
    img = Image.new('RGB', (700, 473), 'white')
    img1 = Image.open(path)
    img1.thumbnail((700, 473))
    img.paste(img1, (int(700 / 2) - int(img1.size[0] / 2), int(473 / 2) - int(img1.size[1] / 2)))
    img.save("preview.png")
    return "preview.png"


class Site:
    def __init__(self, url: str):
        self.url = url
        self.login = None
        self.password = None
        self.session = requests.Session()

    def authorization(self, login: str, password: str):
        self.login = login
        self.password = password

        page_login = self.session.get(self.url + "/login/")
        # parsing csrf_token from page_login
        soup = BeautifulSoup(page_login.text, 'html.parser')

        # if already logged
        if soup.fieldset is None:
            return True

        csrf_token = soup.fieldset.input["value"]
        values = {"_csrf_token": csrf_token,
                  "_username": self.login,
                  "_password": self.password}

        login_status = self.session.post(f"{self.url}/login_check", data=values)

        # bad login or password
        if "Выйти из личного кабинета" not in login_status.text:
            return False

        return True

    def upload_file(self, path_or_bytes: str, title: str, site_path: str):
        # parsing token for upload from page
        page = self.session.get(self.url + site_path)

        page_parse = BeautifulSoup(page.text, 'html.parser').find_all("input")
        page_token = page_parse[2]["value"]

        # upload file
        file_bytes = to_bytes(data=path_or_bytes)
        file = {'form[upload_file]': file_bytes}
        values = {'form[title]': title,
                  'form[save]': '',
                  'form[_token]': page_token}

        status_code = self.session.post(page.url, data=values, files=file).status_code
        if status_code != 406:  # bad
            return False

        return True

    def delete_file(self, file_id: str):
        data = {"Filename": f"/data/file/delete/{file_id}"}
        status_code = self.session.get(f"{self.url}/data/file/delete/{file_id}", headers=data).status_code
        if status_code != 406:  # bad
            return False

        return True

    def get_preview(self, path: str | bytes):
        if config.is_resize_preview:
            path = resize_for_preview(path)

        file_bytes = to_bytes(path)
        preview = self.session.post(f"{self.url}/form/upload_preview", files={"file": file_bytes})
        return preview.json()

    def get_site_preview(self, preview_path):
        preview = ""
        if preview_path:
            # Trying upload preview
            preview = self.get_preview(preview_path).get("thumb")
            if not preview:
                preview = ""
        return preview

    def send_news(self, date=None, news_name=None, tags=None, announcement=None, preview_path=None, content=None):
        if not date:
            date = time.strftime("%Y-%m-%d %H:%M:%S")
        if not news_name:
            news_name = "Тестовая запись"
        if not tags:
            tags = "0"
        if not announcement:
            announcement = ""

        preview = self.get_site_preview(preview_path)

        if not content:
            content = ""

        # get site link: data/form/news/*****/new
        add_button = self.session.get(f"{self.url}/o-nas/novosti")
        get_site_path = BeautifulSoup(add_button.text, 'html.parser')
        site_url = get_site_path.find_all("a")[11].get("href")

        # get token, ord, rel for news
        news_page = self.session.get(self.url + site_url)
        news_parse = BeautifulSoup(news_page.text, 'html.parser').find_all("input")
        news_ord = news_parse[-2]["value"]
        news_token = news_parse[-1]["value"]
        rel = site_url.split("/")[-2]

        value = {
            "form[rel]": rel,
            "form[publish_date]": date,
            "form[name]": news_name,
            "from[tags][]": tags,
            "form[anons]": announcement,
            "form[preview]": preview,
            "form[content]": content,
            "form[save_files]": "{\"files\":[]}",
            "form[ord]": news_ord,
            "form[_token]": news_token
        }

        # upload news
        result_news = self.session.post(news_page.url, data=value)

        if result_news.status_code != 406:
            return False

        return True

    def parsing_files(self, url: str):
        url = self.url + url
        page = self.session.get(url)
        soup = BeautifulSoup(page.text, 'html.parser').find_all("ul")
        files = []
        for s in soup:
            if isinstance(s, bs4.element.Tag):
                for element in s.find_all("li"):
                    if element.get("id"):

                        data = {"file_id": element["id"],
                                "path": element.a.get("href"),
                                "file_name": element.a.text.strip(),
                                "site_path": element.find_all("a")[1].get("href")}

                        files.append(data)
        return files
