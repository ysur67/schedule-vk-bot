from openpyxl import load_workbook
import os
from .FileNamesManager import FileManager
from .FilesDateManager import DateManager
from .TableManager import TableManager

class Table:
    def __init__(self, fileName=""):

        self.__selectedRange = ['A5', 'AD5']

        self.__fileManager = FileManager()

        self.__directory = self.__fileManager.filesPath

        self.__fileNames = self.__fileManager.localFilesNames

        self.__dateManager = DateManager(*self.__fileNames)

        if (self.__isSelectedAndInDirectory(fileName)):
            self.currentFile = fileName
        else:
            self.currentFile = self.__dateManager.latestFile

        self.__earliestFile = self.__dateManager.earliestFile

        self.__dates = self.__dateManager.dates
        
        self.__currentFilePath = self.__directory + "\\" + self.currentFile + ".xlsx"

        self.__workBook = self.__getWorkBook()

        self.__listNames = self.__getWorkSheets()

        self.__firstListName = self.__listNames[0]

        self.__workSheet = self.__getWorkSheet()

        self.__tableManager = TableManager(self.__workSheet)

        self.__groupNames = self.__tableManager.group_names()
        
        self.__lessonsByGroup = self.__tableManager.lessons_by_group

    def __isSelectedAndInDirectory(self, file_):
        return True if file_ != "" and file_ in self.__fileNames else False

    def __getWorkBook(self):
        return load_workbook(self.__currentFilePath)

    def __getWorkSheets(self):
        return self.__workBook.get_sheet_names()

    def __getWorkSheet(self):
        return self.__workBook.get_sheet_by_name(self.__firstListName)

    def groupLessons(self, groupName):
        return self.__lessonsByGroup.get(groupName)

    @property
    def groupNames(self):
        return self.__groupNames
    
    @property
    def earliestFile(self):
        return self.__earliestFile

    @property
    def dates(self):
        dates = {
            self.__earliestFile:self.__dateManager.earliestFileDate,
            self.currentFile:self.__dateManager.latestFileDate,
        }
        return dates

    @property
    def proper_names_for_dialog(self):
        return self.__fileManager.table_names_for_dialog

    @property
    def earliest_file_date(self):
        return self.__dateManager.earliestFileDate

    @property
    def current_file_date(self):
        return self.__dateManager.latestFileDate

    def groupNamesByCourse(self, *range_):
        return self.__tableManager.get_group_names(*range_)
    
    def dialog_name_to_file_name(self, dialog_name):
        date = self.__dateManager.get_date_from_dialog_name(dialog_name)
        return self.__dates.get(date) 

    def date_from_systemname(self, name):
        return self.__dateManager.get_date_from_systemname(name)

    def getProperLessons(self, lessons):
        i = 0
        k = 0
        j = 1
        lessons_ = list(lessons[0])
        #somehow module returns list inside list, this thing needs fix
        lessons_message = ''
        while i<len(lessons_):
            if self.__is_day_of_week(i):
                day_of_week = self.__which_day(k)
                j=1
                k+=1
                lessons_message += f"\n\n{day_of_week}"

            if(lessons_[i]==None):
                lessons_message += '\n{}. '.format(j)   
            else:
                number = str(lessons_[i]).replace('\t', ' ').replace(' ', '')
                try:
                    number = int(number[0])
                except(ValueError):
                    number = 'a'
                if(number in range(0, 10)):
                    lessons_message += '\n'+lessons_[i].replace('  ', '')
                else:
                    lessons_message += '\n' + '{}. '.format(j) + str(lessons_[i]).replace('   ', ' ')
            j+=1
            i+=1
        return lessons_message
    def __is_day_of_week(self, value):
        return True if value % 4 == 0 or value == 0 else False

    def __which_day(self, value):
        day = ""
        if value == 0:
            day = "Понедельник"
        elif value == 1:
            day = "Вторник"
        elif value == 2:
            day = "Среда"
        elif value == 3:
            day = "Четверг"
        elif value == 4:
            day = "Пятница"
        return day

    def __str__(self):
        amount_of_groups = len(self.__groupNames)
        return f"Groups {amount_of_groups}"# change it
