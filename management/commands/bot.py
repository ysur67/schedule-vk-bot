from django.core.management.base import BaseCommand
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from django.conf import settings
from ..modules.vk import API
from ..modules.user import User

from vk_bot.models import TimeTable, Person

class Command(BaseCommand):
    help = "runs vk bot"

    def handle(self, *args, **options):
        print("Hit ctrl+break to stop longpolling")
        bot = VKBot()

class VKBot():
    vk = API()
    for event in vk.longpoll.listen():
        if vk.is_new_message(event):
            user = User(event)

    def __str__(self):
        return str(self.vk)
        