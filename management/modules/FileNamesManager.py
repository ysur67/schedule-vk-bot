import os

class FileManager:
    def __init__(self, *files):
        self.__amountOfFiles = files.__len__()
        self.__directory = os.path.join( os.path.dirname( __file__ ), '..' ) + "\\files"
        self.__localFileNames = self.__getLocalNames()
        self.__fileNames = self.__fillList(files)
            
    def __fillList(self, files):
        return [str(file_) for file_ in files]

    def __getLocalNames(self):
        localNames = os.listdir(self.__directory)
        return [name[:-5] for name in localNames]

    @property
    def filesNames(self):
        return self.__fileNames

    @property
    def amountOfFiles(self):
        return int(self.__amountOfFiles)

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
            dialog_names.append(str(name[0:10] + " " + name[27:]).upper().replace(" ", ""))
        return dialog_names

    def get_proper_name(self, name):
        return name[:10] + " " + name[27:] 


    def __str__(self):
        info = "Object contains {0} file(s)\n".format(self.__amountOfFiles,)
        info += "Directory contains {0} local file(s)".format(len(self.__localFileNames))
        return info   


if __name__ == "__main__":
    man = FileManager("Расписание очное отделение 23.11.20-27.11.20",
        "Расписание очное отделение 30.11.20-04.12.20",)
    print(man.table_names_for_dialog)
