from django.conf import settings

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from .vk import API
from .Table import Table
from .Parser import Parser
from .keyboard import Keyboard
from ...models import TimeTable, Person

class User:
    def __init__(self, event_):
        self.event = event_
        self.user_id = self.event.obj.message['from_id']
        self.message = self.event.obj.message['text'].upper().replace(" ", "")
        self.vk_api = API()
        self.name = self.vk_api.vk.users.get(user_id=self.user_id)[0].get('first_name')
        self.tabel = Table()
        self.time_table = TimeTable.objects.get_or_create(
            name = self.tabel.currentFile,
            date = self.tabel.current_file_date,
        )
        self.person, self.made_now = Person.objects.get_or_create(
            id = self.user_id,
            defaults = {
                'name':self.name,
                'time_table':TimeTable.objects.filter(
                    id=self.time_table[0].pk
                ).get(),
            }
        )
        self.local_time_tables = self.tabel.proper_names_for_dialog
        self.what_in_message()

    def what_in_message(self):
        if self.made_now == True:
            keyboard_ = Keyboard(keyboard_type="COURSES")
            self.vk_api.send_message_keyboard(
                user_id=self.user_id,
                message=f"Добро пожаловать, {self.name}\n"+
                    "Вам было установлено последнeе расписание\n"+
                    'Если хотите изменить, нажмите "Изменить расписание"',
                keyboard=keyboard_.get_keyboard(),
            )
        elif self.message == "НАЧАТЬ" or self.message == "НАЗАД":
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
            Person.objects.filter(id=self.user_id).update(time_table=_[0].pk)
            # I don't know why should I get id from tuple like I did it above
            # but it works just fine :)
            keyboard_ = Keyboard(keyboard_type="COURSES")
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
            if(p.time_table.name in self.tabel.dates):
                tabel_name = self.tabel.dialog_file_name(p.time_table.name)
            else:
                tabel_name = self.tabel.dialog_file_name(self.tabel.currentFile)
                self.vk_api.send_message(
                    message="Ваш выбор расписания устарел!\n"+
                        "В данный момент вам будет выбрано последнее расписание\n"+
                        "Не забудьте его поменять!",
                    user_id=self.user_id,
                    )
            system_name = self.tabel.dialog_name_to_file_name(tabel_name)
            chosen_table = Table(system_name)
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
        names_for_comparison = [name.replace(' ', '').upper() for name in self.local_time_tables]
        return True if message in names_for_comparison else False

    def is_course(self, message):
        return True if message[1:] == "КУРС" and len(message) == 5 else False

    def is_group_name(self, message):
        return True if self.message in self.tabel.groupNames else False

