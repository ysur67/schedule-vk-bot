from openpyxl import load_workbook
import os
from .FileNamesManager import FileManager
from .FilesDateManager import DateManager
from .TableManager import TableManager

class Table:
    def __init__(self, fileName=""):

        self.__file_manager = FileManager()

        self.__directory = self.__file_manager.filesPath

        self.__fileNames = self.__file_manager.localFilesNames

        self.__dates_manager = DateManager(*self.__fileNames)

        if self.__is_selected_and_in_directory(fileName):
            self._current_file = fileName
        else:
            self._current_file = self.__dates_manager.latestFile

        self._earliest_file = self.__dates_manager.earliestFile

        self.__dates = self.__dates_manager.dates
        
        self.__current_file_path = self.__directory + "\\" + self._current_file + ".xlsx"

        self.__work_book = self.__Work_Book()

        self.__list_names = self.__get_work_sheets()

        self.__firstListName = self.__list_names[0] 
        # schedule is always placed in the first list of workbook

        self.__work_sheet = self.__Work_Sheet()

        self.__time_table_manager = TableManager(self.__work_sheet)

        self.__group_names = self.__time_table_manager.group_names()
        
        self._lessons_by_group = self.__time_table_manager.lessons_by_group

    def __is_selected_and_in_directory(self, file_):
        return True if file_ != "" and file_ in self.__fileNames else False

    def __Work_Book(self):
        return load_workbook(self.__current_file_path)

    def __get_work_sheets(self):
        return self.__work_book.get_sheet_names()

    def __Work_Sheet(self):
        return self.__work_book.get_sheet_by_name(self.__firstListName)

    def groupLessons(self, groupName):
        return self._lessons_by_group.get(groupName)

    def groupNamesByCourse(self, *range_):
        return self.__time_table_manager.get_group_names(*range_)

    def file_name_to_dialog_name(self, name):
        return self.__file_manager.get_proper_name(name)
    
    def dialog_name_to_file_name(self, dialog_name):
        date = self.__dates_manager.get_date_from_name(dialog_name)
        return self.__dates.get(date) 

    def date_from_systemname(self, name):
        return self.__dates_manager.get_date_from_name(name)

    def get_proper_lessons(self, lessons):
        return self.__time_table_manager.get_proper_lessons(lessons[0])

    def pop_file(self, file_name):
        os.remove(str(self.__directory+'\\'+file_name+".xlsx"))

    @property
    def group_names(self):
        return self.__group_names
        
    @property
    def dates(self):
        dates = self.__dates_manager.dates.values()
        return dates

    @property
    def proper_names_for_dialog(self):
        return self.__file_manager.table_names_for_dialog

    @property
    def earliest_file_date(self):
        return self.__dates_manager.earliestFileDate

    @property
    def current_file_date(self):
        return self.__dates_manager.latestFileDate
