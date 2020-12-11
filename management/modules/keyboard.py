from .Table import Table

from vk_api.keyboard import VkKeyboard, VkKeyboardColor

class Keyboard:
    settings = dict(one_time=False, inline=False)

    def __init__(self, keyboard_type, message=""):
        self.table_manager = Table()
        if keyboard_type == "BEGIN":
            self.keyboard = self.Begin_Keyboard()
        elif keyboard_type == "COURSES":
            self.keyboard = self.Courses_Keyboard()
        elif keyboard_type == "GROUPS":
            self.keyboard = self.Groups_Keyboard(message)
        elif keyboard_type == "TIMETABLE":
            self.keyboard = self.TimeTable_Keyboard()
        elif keyboard_type == "SETTINGS":
            self.keyboard = self.Settings_Keyboard()
        elif keyboard_type == "NOTIFY":
            self.keyboard = self.Notify_Keyboard()
        elif keyboard_type == "ADMIN":
            self.keyboard = self.Admin_Keyboard()
    
    def Begin_Keyboard(self):
        keyboard = VkKeyboard(**self.settings)
        keyboard.add_button('Начать')
        return keyboard

    def Courses_Keyboard(self):
        keyboard = VkKeyboard(**self.settings)
        keyboard.add_button('1 курс')
        keyboard.add_line()
        keyboard.add_button('2 курс')
        keyboard.add_line()
        keyboard.add_button('3 курс')
        keyboard.add_line()
        keyboard.add_button('4 курс')
        keyboard.add_line()
        keyboard.add_button(label="Настройки", color=VkKeyboardColor.PRIMARY)
        return keyboard

    def Groups_Keyboard(self, answer):
        keyboard_ = VkKeyboard(**self.settings)
        group_names_by_course = []
        if (answer == "1КУРС") or answer=="1":
            group_names_by_course = self.table_manager.groupNamesByCourse("C5", "K5")
        elif answer=="2КУРС" or answer=="2":
            group_names_by_course = self.table_manager.groupNamesByCourse("L5", "S5")
        elif answer=="3КУРС" or answer=="3":
            group_names_by_course = self.table_manager.groupNamesByCourse("T5", "AB5")
        elif answer=="4КУРС" or answer=="4":
            group_names_by_course = self.table_manager.groupNamesByCourse("AC5", "AD5")
        i = 0
        while i<len(group_names_by_course):
            keyboard_.add_button(group_names_by_course[i])
            keyboard_.add_line()
            i+=1
        keyboard_.add_button(label= "Назад", color=VkKeyboardColor.PRIMARY)
        return keyboard_

    def TimeTable_Keyboard(self):
        keyboard_ = VkKeyboard(**self.settings)
        time_tables = []
        i = 0
        dates = self.table_manager.dates
        for key in dates:
            time_tables.append(self.__proper_text_for_button(str(key)))
        while i < len(time_tables):
            keyboard_.add_button(time_tables[i])
            keyboard_.add_line()
            i+=1
        keyboard_.add_button(label="Отмена, к настройкам", color=VkKeyboardColor.PRIMARY)
        return keyboard_

    def __proper_text_for_button(self, text):
        return text[0:10] + " " + text[27:]

    def Settings_Keyboard(self):
        keyboard_ = VkKeyboard(**self.settings)
        keyboard_.add_button("Изменить расписание")
        keyboard_.add_line()
        keyboard_.add_button("Настройка уведомлений")
        keyboard_.add_line()
        keyboard_.add_button("Статус")
        keyboard_.add_line()
        keyboard_.add_button(label="Назад", color=VkKeyboardColor.PRIMARY)
        return keyboard_

    def Notify_Keyboard(self):
        keyboard_ = VkKeyboard(**self.settings)
        keyboard_.add_button(
            label="Получать уведомления", 
            color=VkKeyboardColor.POSITIVE,
            )
        keyboard_.add_line()
        keyboard_.add_button(
            label="Не получать уведомлений", 
            color=VkKeyboardColor.NEGATIVE,
            )
        keyboard_.add_line()
        keyboard_.add_button(label="Отмена, к настройкам", color=VkKeyboardColor.SECONDARY)
        return keyboard_

    def Admin_Keyboard(self):
        keyboard_ = VkKeyboard(**self.settings)
        time_tables = []
        i = 0
        dates = self.table_manager.dates
        for key in dates:
            time_tables.append(self.__proper_text_for_button(str(key)))
        while i < len(time_tables):
            keyboard_.add_button(time_tables[i]+" админ")
            keyboard_.add_line()
            i+=1
        keyboard_.add_button(label="Назад", color=VkKeyboardColor.PRIMARY)
        return keyboard_

    def get_keyboard(self):
        return self.keyboard
        