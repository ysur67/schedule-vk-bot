from django.conf import settings
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard

class API:
    vk_session = vk_api.VkApi(
            token=settings.TOKEN
            )
    vk = vk_session.get_api()
    admins = settings.ADMINS
    longpoll = VkBotLongPoll(
            vk_session, 
            group_id=settings.GROUP_ID,
            )

    # def __init__(self):
    #     self.vk_session = vk_api.VkApi(
    #         token=settings.TOKEN
    #         )
    #     self.vk = self.vk_session.get_api()
    #     self.api_version = settings.API_VERSION
    #     self.admins = settings.ADMINS
    #     self.longpoll = VkBotLongPoll(
    #         self.vk_session, 
    #         group_id=settings.GROUP_ID,
    #         )

    def send_message(self, message, user_id):
        try:
            self.vk.messages.send(
                user_id=int(user_id),
                random_id=get_random_id(),
                peer_id = int(user_id),
                message=message
                )
        except Exception:
            self.vk.messages.send(
                user_id = int(self.admins[0]),
                random_id=get_random_id(),
                peer_id = int(self.admins[0]),
                message="*(" + str(user_id) + ") не включил сообщения от сообщества!" 
            )
    
    def send_message_keyboard(self, message, user_id, keyboard):
        try:
            self.vk.messages.send(
                user_id=int(user_id),
                random_id=get_random_id(),
                peer_id = int(user_id),
                message=message,
                keyboard= keyboard.get_keyboard(),
                )
        except Exception:
            self.vk.messages.send(
                user_id = int(self.admins[0]),
                random_id=get_random_id(),
                peer_id = int(self.admins[0]),
                message="*(" + str(user_id) + ") не включил сообщения от сообщества!" 
            )

    def is_new_message(self, event):
        return True if event.type == VkBotEventType.MESSAGE_NEW else False
