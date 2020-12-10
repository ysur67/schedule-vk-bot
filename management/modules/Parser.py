import requests
from bs4 import BeautifulSoup
import os
import re
from .botExceptions import ModuleException
from .FileNamesManager import FileManager
from .FilesDateManager import DateManager

class Parser:
    def __init__(self):
        self.__url = 'https://vkk.edu.ru/raspisanie-zanyatiy'

        self.__headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.234', 'accept': '*/*'}

        self.__html= self.__getURL()

        self.__soup = BeautifulSoup(self.__html.text, 'html.parser')

        self.__tags = self.__getTags()

        self.__hrefList = self.__getFileHrefs()

        self.__fileNames = self.__getFileNames()
        
        self.time_tables_names = self.Time_Tables(*self.__fileNames)

        #self.__fileManager = FileManager(self.__fileNames[0], self.__fileNames[1])
        self.__file_manager = FileManager(*self.time_tables_names)

        self.__dateManager = DateManager(*self.__file_manager.filesNames)
        
        self.__currentTimeTableName = self.__dateManager.latestFile + ".xlsx"

        self.__linkToTables = self.__getLinks()

        self.__directory = self.__file_manager.filesPath

        self.__filePath = os.path.join(self.__directory, self.__currentTimeTableName)

        self.__downloadRequest = requests.get(
            self.__linkToTables.get(self.__dateManager.latestFile),
            allow_redirects=True,
            )

        open(self.__filePath, 'wb').write(self.__downloadRequest.content)

    def __getURL(self):
        try:
            link = requests.get(self.__url, self.__headers)
            return link
        except Exception:
            raise ModuleException("Your link might be broken or server is down")

    def __getTags(self):
        return self.__soup.find_all("span", class_='file')

    def __getFileHrefs(self):
        return [span.find('a').get('href') for span in self.__tags]

    def __getFileNames(self):
        fileNames = [span.find('a').text for span in self.__tags]
        return fileNames

    def Time_Tables(self, *file_names):
        proper_files = []
        is_time_table = lambda name: proper_files.append(name) if " очное" in name else None
        [is_time_table(name) for name in file_names]
        return proper_files

    def __getLinks(self):
        if len(self.__file_manager.filesNames)<3:
            return dict(zip(self.__file_manager.filesNames, self.__hrefList[0:2]))
        else:
            return dict(zip(self.__file_manager.filesNames, self.__hrefList[0:3]))


    def __getCurrentFileName(self):
        return self.__dateManager.latestFile

    def __removeEarliest(self):
        locFileManager = FileManager()
        locDatesManager = DateManager(*locFileManager.localFilesNames)
        os.remove(str(self.__directory+'\\'+locDatesManager.earliestFile+".xlsx"))

    @property
    def isNewFileLoaded(self):
        return True if self.__hasMoreThanTwoFiles else False

    @property
    def latestFile(self):
        return self.__dateManager.latestFile

    @property
    def earliestFile(self):
        return self.__dateManager.earliestFile

    def __str__(self):
        info = "The module has uploaded a new file = {0}\n".format(self.__hasMoreThanTwoFiles)
        info += "Earliest file in directory '{}'\n".format(self.__dateManager.earliestFile)
        info += "Latest file in directory '{}'\n".format(self.__dateManager.latestFile)
        return info

if __name__ == "__main__":
    par = Parser()
    print(par.time_tables_names)