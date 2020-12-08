from django.conf import settings

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from .vk import API
from .Table import Table
from .Parser import Parser
from ...models import TimeTable, Person

class User:
    def __init__(self, event_):
        self.event = event_
        self.user_id = self.event.obj.message['from_id']
        self.random_id = get_random_id()
        self.message = self.event.obj.message['text'].upper().replace(" ", "")
        self.vk_api = API()
        self.tabel = Table()
        self.time_table = TimeTable.objects.get_or_create(
            name = self.tabel.currentFile,
            date = self.tabel.current_file_date,
        )
        self.person = Person.objects.get_or_create(
            id = self.user_id,
            time_table=TimeTable.objects.filter(
                id=self.time_table[0].pk
            ).get(),
        )
        self.local_time_tables = self.tabel.proper_names_for_dialog
        self.what_in_message()

    def what_in_message(self):
        if self.message == "НАЧАТЬ" or self.message == "НАЗАД":
            keyboard_ = Keyboard(keyboard_type="COURSES")
            self.vk_api.send_message_keyboard(
                message = "Главное меню",
                user_id = self.event.obj.message['from_id'],
                keyboard = keyboard_.get_keyboard(),
                )
        elif self.message == "ИЗМЕНИТЬРАСПИСАНИЕ":
            keyboard_ = Keyboard(keyboard_type="TIMETABLE")
            self.vk_api.send_message_keyboard(
                user_id = self.user_id,
                message = "Выберите расписание",
                keyboard = keyboard_.get_keyboard(),
            )
        elif self.is_time_table(self.message):
            time_table_systemname = self.tabel.dialog_name_to_file_name(self.message)
            _ = TimeTable.objects.get_or_create(
                name = time_table_systemname,
                date = self.tabel.date_from_systemname(time_table_systemname),  
            )
            Person.objects.filter(id=self.user_id).update(time_table=str(_[0].pk))
            # I don't know why should I get id from tuple like I did it above
            # but it works just fine :)
            keyboard_ = Keyboard(keyboard_type="BEGIN")
            self.vk_api.send_message_keyboard(
                user_id = self.user_id,
                message = "Ваше расписание обновлено",
                keyboard = keyboard_.get_keyboard(),
            )
        elif self.is_course(self.message):
            keyboard_ = Keyboard(keyboard_type="GROUPS", message=self.message)
            self.vk_api.send_message_keyboard(
                user_id = self.user_id,
                message = "Выберите группу",
                keyboard = keyboard_.get_keyboard(),
            )
        elif self.is_group_name(self.message):
            p = Person.objects.get(
                id = self.user_id
            )
            tabel_name = str(p.time_table.name)
            chosen_table = Table(tabel_name)
            lessons = chosen_table.groupLessons(self.message)
            lessons_for_dialog = chosen_table.getProperLessons(lessons)
            group_name = self.message
            self.vk_api.send_message(
                user_id = self.user_id,
                message = tabel_name + "\n" 
                    + "Группа: " + group_name + 
                    "\n" + lessons_for_dialog,
            )
        elif self.message == "НАСТРОЙКАУВЕДОМЛЕНИЙ":
            keyboard_ = Keyboard(keyboard_type="SETTINGS")
            self.vk_api.send_message_keyboard(
                user_id = self.user_id,
                message = "Если хотите отменить, нажмите 'Назад'",
                keyboard = keyboard_.get_keyboard()
            )
        elif self.message == "НЕПОЛУЧАТЬУВЕДОМЛЕНИЙ":
            keyboard_ = Keyboard(keyboard_type="BEGIN")
            Person.objects.filter(id=self.user_id).update(send_notifications=False)
            self.vk_api.send_message_keyboard(
                user_id = self.user_id,
                message = "Вы больше не будете получать уведомлений",
                keyboard = keyboard_.get_keyboard(),
            )
        elif self.message == "ПОЛУЧАТЬУВЕДОМЛЕНИЯ":
            keyboard_ = Keyboard(keyboard_type="BEGIN")
            Person.objects.filter(id=self.user_id).update(send_notifications=True)
            self.vk_api.send_message_keyboard(
                user_id = self.user_id,
                message = "Теперь вы будете получать уведомления",
                keyboard = keyboard_.get_keyboard(),
            )
        elif self.message == "ОБНОВИТЬ":
            #p = Parser()
            f = True
            #if p.isNewFileLoaded:
            # Parser works fine
            # but there are no timetables
            # on site 
            if f:
                self.vk_api.send_message(
                    user_id = self.user_id,
                    message = "Найдено новое расписание, обновляю..."
                )
                _ = Person.objects.filter(send_notifications=True)
                for person in _:
                    self.vk_api.send_message(
                        user_id = person.pk,
                        message = "Появилось новое расписание"
                    )
            else:
                self.vk_api.send_message(
                    user_id = self.user_id,
                    message = "Нового расписания не найдено, отмена..."
                )
        else:
            keyboard_ = Keyboard(keyboard_type="BEGIN")
            self.vk_api.send_message_keyboard(
                user_id = self.user_id,
                message = 'Я вас не понимаю\nПожалуйста, пользуйтесь кнопками\n'+
                    'Что бы продолжить нажмите "Начать"',
                keyboard = keyboard_.get_keyboard(),
            )

    def is_time_table(self, message):
        return True if message in self.local_time_tables else False

    def is_course(self, message):
        return True if message[1:] == "КУРС" and len(message) == 5 else False

    def is_group_name(self, message):
        return True if self.message in self.tabel.groupNames else False

class Keyboard:
    settings = dict(one_time=False, inline=False)

    table_manager = Table()

    def __init__(self, keyboard_type, message=""):
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
        keyboard.add_button(label='Изменить расписание')
        keyboard.add_line()
        keyboard.add_button(label='Настройка уведомлений')
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
        keyboard_.add_button(label="Назад", color=VkKeyboardColor.PRIMARY)
        return keyboard_

    def __proper_text_for_button(self, text):
        return text[0:10] + " " + text[27:]

    def Settings_Keyboard(self):
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
        keyboard_.add_button(label="Назад", color=VkKeyboardColor.SECONDARY)
        return keyboard_

    def get_keyboard(self):
        return self.keyboard
    