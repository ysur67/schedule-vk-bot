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
import re

class User:
    def __init__(self, event_):
        self.event = event_
        self.user_id = self.event.obj.message['from_id']
        self.message = self.event.obj.message['text'].upper().replace(" ", "")
        self.api = API()
        self.name = self.api.vk.users.get(user_id=self.user_id)[0].get('first_name')
        self.last_name = self.api.vk.users.get(user_id=self.user_id)[0].get('last_name')
        self.tabel = Table()
        if self.tabel.dates == None:
            Parser()
        self.time_table = TimeTable.objects.get_or_create(
            name = self.tabel._current_file,
            date = self.tabel.current_file_date,
        )
        self.person, self.new_user = Person.objects.get_or_create(
            id = self.user_id,
            defaults = {
                'name':self.name,
                'last_name':self.last_name,
                'time_table':TimeTable.objects.filter(
                    id=self.time_table[0].pk
                ).get(),
            }
        )
        self.local_time_tables = self.tabel.proper_names_for_dialog
        self.what_in_message()

    def what_in_message(self):
        if self.new_user:
            keyboard_ = Keyboard(keyboard_type="COURSES")
            self.api.send_message_keyboard(
                user_id=self.user_id,
                message=self.hello_message(),
                keyboard=keyboard_.get_keyboard(),
            )
        elif self.is_begin_message(self.message):
            keyboard_ = Keyboard(keyboard_type="COURSES")
            self.api.send_message_keyboard(
                message = "Главное меню",
                user_id = self.event.obj.message['from_id'],
                keyboard = keyboard_.get_keyboard(),
                )
        elif self.message == "ИЗМЕНИТЬРАСПИСАНИЕ":
            keyboard_ = Keyboard(keyboard_type="TIMETABLE")
            self.api.send_message_keyboard(
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
            self.api.send_message_keyboard(
                user_id = self.user_id,
                message = "Ваше расписание обновлено",
                keyboard = keyboard_.get_keyboard(),
            )
        elif self.is_course(self.message):
            keyboard_ = Keyboard(keyboard_type="GROUPS", message=self.message)
            self.api.send_message_keyboard(
                user_id = self.user_id,
                message = "Выберите группу",
                keyboard = keyboard_.get_keyboard(),
            )
        elif self.is_group_name(self.message):
            self.lessons_handler()
        elif self.message == "НАСТРОЙКИ" or self.message=="ОТМЕНА,КНАСТРОЙКАМ":
            keyboard_ = Keyboard(keyboard_type="SETTINGS")
            self.api.send_message_keyboard(
                user_id=self.user_id,
                message='Если хотите выйти, нажмите "Назад"',
                keyboard=keyboard_.get_keyboard(),
            )
        elif self.message == "НАСТРОЙКАУВЕДОМЛЕНИЙ":
            keyboard_ = Keyboard(keyboard_type="NOTIFY")
            self.api.send_message_keyboard(
                user_id = self.user_id,
                message = "Если хотите отменить, нажмите 'Назад'",
                keyboard = keyboard_.get_keyboard()
            )
        elif self.message == "НЕПОЛУЧАТЬУВЕДОМЛЕНИЙ":
            Person.objects.filter(id=self.user_id).update(send_notifications=False)
            self.api.send_message(
                user_id = self.user_id,
                message = "Вы больше не будете получать уведомлений",
            )
        elif self.message == "ПОЛУЧАТЬУВЕДОМЛЕНИЯ":
            Person.objects.filter(id=self.user_id).update(send_notifications=True)
            self.api.send_message(
                user_id = self.user_id,
                message = "Теперь вы будете получать уведомления",
            )
        elif self.message == "ОБНОВИТЬ":
            if self.user_is_admin():
                self.update_handler()
                self.api.send_message(
                    user_id = self.user_id,
                    message = "Обновление расписаний..."
                )
            else:
                self.not_an_admin_error(self.user_id)
        elif self.message == "УДАЛИТЬ":
            if self.user_is_admin():
                keyboard_ = Keyboard(keyboard_type="ADMIN")
                self.api.send_message_keyboard(
                    user_id = self.user_id,
                    message = "Выберите, какое расписание удалить",
                    keyboard = keyboard_.get_keyboard(),
                )
            else:
                self.not_an_admin_error(self.user_id)
        elif self.is_delete_message():
            if self.user_is_admin():
                self.delete_file_handler()
                self.api.send_message(
                    user_id=self.user_id,
                    message="Выбранное вами расписание было удалено",
                )
            else:
                self.not_an_admin_error(self.user_id)
        elif self.message == "СТАТУС":
            answer = self.status_handler()
            self.api.send_message(
                user_id=self.user_id,
                message=answer,
            )
        else:
            keyboard_ = Keyboard(keyboard_type="BEGIN")
            self.api.send_message_keyboard(
                user_id = self.user_id,
                message = 'Я вас не понимаю\nПожалуйста, пользуйтесь кнопками\n'+
                    'Чтобы продолжить, нажмите "Начать"',
                keyboard = keyboard_.get_keyboard(),
            )

    def hello_message(self):
        message = f"Добро пожаловать, {self.name} {self.last_name}\n"
        message += "Вам было установлено последнeе расписание\n"
        message += 'Если хотите изменить, нажмите "Изменить расписание"\n'
        message += '\nПо умолчанию вы не получаете уведомлений\n'
        message += 'Поэтому, если хотите это поменять, зайдите в настройки'
        # I don't know why
        # but constructions like this one
        # message = "abc" + 
        #   "cba"
        # isn't working here
        return message

    def is_begin_message(self, message):
        return True if self.message == "НАЧАТЬ" or self.message == "НАЗАД" or self.message == "ГЛАВНОЕМЕНЮ" else False

    def is_time_table(self, message):
        names_for_comparison = [name.replace(' ', '').upper() for name in self.local_time_tables]
        return True if message in names_for_comparison else False

    def is_course(self, message):
        return True if message[1:] == "КУРС" and len(message) == 5 else False

    def is_group_name(self, message):
        return True if self.message in self.tabel.group_names else False

    def is_time_table_exists(self, person):
        return True if person.time_table != None and person.time_table.name in self.tabel.dates else False

    def is_delete_message(self):
        return True if "АДМИН" in self.message and len(self.message)>5 else False

    def user_is_admin(self):
        return True if self.user_id in self.api.admins else False

    def lessons_handler(self):
        person = Person.objects.get(
                id = self.user_id
            )
        if self.is_time_table_exists(person):
            tabel_name = self.tabel.file_name_to_dialog_name(person.time_table.name)
        else:
            tabel_name = self.tabel.file_name_to_dialog_name(self.tabel._current_file)
            Person.objects.filter(id=self.user_id).update(time_table=self.time_table[0])
            self.api.send_message(
                message=self.outdated_message(),
                user_id=self.user_id,
                )
        system_name = self.tabel.dialog_name_to_file_name(tabel_name)
        chosen_table = Table(system_name)
        lessons = chosen_table.groupLessons(self.message)
        lessons_for_dialog = chosen_table.get_proper_lessons(lessons)
        group_name = self.message
        self.api.send_message(
            user_id = self.user_id,
            message = tabel_name + "\n" 
                + "Группа: " + group_name +
                "\n" + lessons_for_dialog,
        )

    def outdated_message(self):
        message = "&#10071; Ваш выбор расписания устарел, оно было удалено\n"
        message += "В данный момент вам выбрано последнее расписание\n"
        message += "Не забудьте его поменять, если вам необходимо другое!"
        return message

    def delete_file_handler(self):
        dialog_file_name = re.sub(r'АДМИН', "", self.message).title()
        file_to_delete = self.tabel.dialog_name_to_file_name(dialog_file_name)
        self.tabel.pop_file(file_to_delete)

    def update_handler(self):
        Parser()
        self.notify_users()

    def notify_users(self):
        persons_notify_true = Person.objects.filter(send_notifications=True)
        for person in persons_notify_true:
            self.api.send_message(
                user_id = person.pk,
                message = "Появилось новое расписание"
            )

    def status_handler(self):
        p = Person.objects.get(
                id = self.user_id
            )
        message = "\nВыбранное расписание:\n"
        if p.time_table == None:
            message+="&#10071; Выбранное вами расписание было удалено, пожалуйста, выберите другое\n"
        else:
            message += self.tabel.file_name_to_dialog_name(p.time_table.name) + "\n\n"
        message += "Уведомления о новом расписании - "
        if p.send_notifications:
            message += "&#9989; Включены"
        else:
            message += "&#10060; Отключены" 
        return message

    def not_an_admin_error(self, user_id):
        self.api.send_message(
            user_id=user_id,
            message="Вы не являетесь администратором"
        )

