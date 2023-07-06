from django.core.management import BaseCommand
from bot.main import bot
class Command(BaseCommand):

    def handle(self, *args, **options):
        # here logic for running bot
        bot.infinity_polling(none_stop=True, skip_pending=True)
