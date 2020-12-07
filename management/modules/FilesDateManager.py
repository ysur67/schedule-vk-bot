from datetime import datetime

class DateManager:
    def __init__(self, *filesNames):
        self.__amountOfFiles = filesNames.__len__()
        self.__filesNames = filesNames
        self.__dates = self.__fillList()
        self.__earliestFile = self.__dates.get(self.__getEarliestDate(self.__dates))
        self.__latestFile = self.__dates.get(self.__getLatestDate(self.__dates))
    
    def __fillList(self):
        filesDates = {}
        for name in self.__filesNames:
            date = self.__getDateFromName(name)
            filesDates[date] = name
        return filesDates

    def __getDateFromName(self, fileName):
        date = datetime.strptime(fileName[27:35], "%d.%m.%y")
        return date

    def __getEarliestDate(self, dates):
        return min(dates)
    
    def __getLatestDate(self, dates):
        return max(dates)

    def get_date_from_dialog_name(self, name):
        return datetime.strptime(name.replace(" ","")[10:18], "%d.%m.%y")

    def get_date_from_systemname(self, name):
        return self.__getDateFromName(name)

    @property
    def earliestFile(self):
        return self.__earliestFile

    @property
    def latestFile(self):
        return self.__latestFile

    @property
    def earliestFileDate(self):
        return min(self.__dates)

    @property
    def latestFileDate(self):
        return max(self.__dates)
    
    @property
    def dates(self):
        return self.__dates

    def __str__(self):
        info = "The earliest file you've given is {0}\n".format(self.__earliestFile)
        info += "The latest file you've given is {0}\n".format(self.__latestFile)
        info += "All the files you've given and their dates: \n"
        info += str(self.__dates)
        return info
        
if __name__ == "__main__":
    date = DateManager("Расписание очное отделение 01.12.20-27.11.20", 
        "Расписание очное отделение 30.11.20-04.12.20",)
    # print(date.dates)
    # print(date.latestFile)
    # print(date.latestFileDate)
    print(date.get_date_from_dialog_name("Расписание 30.11.20-04.12.20"))
