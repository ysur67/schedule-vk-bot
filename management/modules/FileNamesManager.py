import os
import re

class FileManager:
    def __init__(self, *files):
        self.__directory = os.path.join( os.path.dirname( __file__ ), '..' ) + "\\files"
        self.__localFileNames = self.__getLocalNames()
        self.__files = files
        self.__fileNames = self.__fillList(files)
            
    def __fillList(self, files):
        return [str(file_) for file_ in files]

    def __getLocalNames(self):
        localNames = os.listdir(self.__directory)
        return [name[:-5] for name in localNames]

    def update_all(self):
        self.__localFileNames = self.__getLocalNames()
        self.__fileNames = self.__fillList(self.__files)

    @property
    def filesNames(self):
        return self.__fileNames

    @property
    def filesPath(self):
        return self.__directory

    @property
    def localFilesNames(self):
        return self.__localFileNames

    @property
    def table_names_for_dialog(self):
        dialog_names = []
        for name in self.__localFileNames:
            dialog_names.append(self.pop_extra_info(name))
        return dialog_names

    def get_proper_name(self, name):
        return self.pop_extra_info(name)

    def pop_extra_info(self, name):
        return re.sub(r'очное отделение', '', name).replace('   ', '')

    def __str__(self):
        info = "Directory contains {0} local file(s)".format(len(self.__localFileNames))
        return info   

if __name__ == "__main__":
    file_man = FileManager(
        "Расписание очное отделение 01.12.20-27.11.20", 
        "Расписание очное отделение 30.11.20-04.12.20",
    )
    print(file_man.table_names_for_dialog)

