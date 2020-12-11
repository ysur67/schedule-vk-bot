import requests
from bs4 import BeautifulSoup
import os
import re
from .botExceptions import ModuleException
from .FileNamesManager import FileManager
from .FilesDateManager import DateManager

class Parser:
    def __init__(self):
        self._url = 'https://vkk.edu.ru/raspisanie-zanyatiy'

        self.__headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.234',
            'accept': '*/*'
            }

        self.html= self.get_link()

        self._soup = BeautifulSoup(self.html.text, 'html.parser')

        self._tags = self.__getTags()

        self.__all_links = self.File_Links()

        self.__all_files_names = self.__File_Names()
        
        self.time_tables_names = self.Time_Tables(*self.__all_files_names)
        
        self.links_to_time_tables = self.Links()

        self.__file_manager = FileManager(*self.time_tables_names)

        self.__date_manager = DateManager(*self.__file_manager.filesNames)

        self.__links_to_tables = self.Links()

        self.__directory = self.__file_manager.filesPath
        
        self.load_proper_files()

    def get_link(self):
        try:
            link = requests.get(self._url, self.__headers)
            return link
        except Exception:
            raise ModuleException("Your link might be broken or server is down")

    def __getTags(self):
        return self._soup.find_all("span", class_='file')

    def File_Links(self):
        return [span.find('a').get('href') for span in self._tags]

    def __File_Names(self):
        fileNames = [span.find('a').text for span in self._tags]
        return fileNames

    def Time_Tables(self, *file_names):
        proper_files = []
        is_time_table = lambda name: proper_files.append(name) if " очное" in name else None
        [is_time_table(name) for name in file_names]
        return proper_files

    def Links(self):
        return dict(zip(self.time_tables_names, self.__all_links))

    def __getCurrentFileName(self):
        return self.__date_manager.latestFile

    def load_proper_files(self):
        for key in self.links_to_time_tables:
            download_request = requests.get(
                self.links_to_time_tables.get(key),
                allow_redirects=True,
                )
            file_path = os.path.join(self.__directory, key) + ".xlsx"
            open(file_path, 'wb').write(download_request.content)
