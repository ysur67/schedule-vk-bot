from openpyxl import load_workbook
import os

class TableManager:
    def __init__(self, work_sheet):
        self.work_sheet = work_sheet
        self.range_ = ['A5', 'AD5']
        self.groups_and_locations = self.get_groups_to_cells(*self.range_)
        self.lessons_by_group = self.get_lessons_by_group()

    def get_groups_to_cells(self, range_start, range_end):
        return dict(zip(
            self.get_group_names(range_start, range_end), 
            self.get_cells_of_names(range_start, range_end))
            )

    def get_group_names(self, range_start, range_end):
        group_names = []
        for cellObj in self.work_sheet[range_start:range_end]:
            for cell in cellObj:
                if(cell.value!=None):
                    group_names.append(cell.value.upper().replace(' ', ''))
        return group_names

    def get_cells_of_names(self, range_start, range_end):
        group_cells = []
        for cellObj in self.work_sheet[range_start:range_end]:
            for cell in cellObj:
                if(cell.value!=None):
                    group_cells.append(cell.coordinate)
        return group_cells

    def get_lessons_by_group(self):
        lessons_by_group = {}
        for group_name in self.groups_and_locations:
            group_lessons = []
            group_lessons.append(self._get_group_lessons(
                self.groups_and_locations.get(group_name)
                ))
            lessons_by_group[group_name] = group_lessons
        return lessons_by_group

    def _get_group_lessons(self, location):
        chars_of_location = self.get_location_chars(location)
        group_lessons_range = self.get_groups_lessons_range(chars_of_location)
        group_lessons = self.get_groups_lessons(group_lessons_range)
        return group_lessons

    def get_location_chars(self, string):
        return string[0] if len(string)<3 else string[0:2]
    
    def get_groups_lessons_range(self, chars_of_location):
        return ["{}9".format(chars_of_location), "{}28".format(chars_of_location)]

    def get_groups_lessons(self, location_range):
        group_lessons = []
        for cellObj in self.work_sheet[location_range[0]:location_range[1]]:
            for cell in cellObj:
                group_lessons.append(cell.value)
        return group_lessons

    def get_lessons(self, group_name):
        return self.lessons_by_group.get(group_name)

    def group_names(self):
        return list(self.groups_and_locations.keys())