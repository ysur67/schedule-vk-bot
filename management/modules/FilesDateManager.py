from datetime import datetime
import re

class DateManager:
    def __init__(self, *filesNames):
        #self.__amountOfFiles = filesNames.__len__()
        self.__filesNames = filesNames
        self.__dates = self.__all_dates()
        self.__earliestFile = self.__dates.get(self.__getEarliestDate(self.__dates))
        self.__latestFile = self.__dates.get(self.__getLatestDate(self.__dates))
    
    def __all_dates(self):
        files_dates = {}
        for name in self.__filesNames:
            date = self.get_date_from_name(name)
            files_dates[date] = name
        return files_dates

    def get_date_from_name(self, fileName):
        get_date = lambda date: datetime.strptime(date, "%d.%m.%y")
        string_dates = re.findall(r'\d{2}.\d{2}.\d{2}', fileName)
        proper_dates = [get_date(date) for date in string_dates]
        return min(proper_dates)
        # I will always use first date from names
        # so it means, this is the first one

    def __getEarliestDate(self, dates):
        return min(dates)
    
    def __getLatestDate(self, dates):
        return max(dates)        

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
    date = DateManager(
        "Расписание очное отделение 01.12.20-27.11.20", 
        "Расписание очное отделение 30.11.20-04.12.20",
        )
    #print(date.File)
    print(date)
    print(date.get_date_from_name('Расписание 30.11.20-04.12.20'))
