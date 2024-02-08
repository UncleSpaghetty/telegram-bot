from django.core.management.base import BaseCommand

from . import main 

class Command(BaseCommand):

	def handle(self, *args, **options):
		# main.run()
		main.main()
