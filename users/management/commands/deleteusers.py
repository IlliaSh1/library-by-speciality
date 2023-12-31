from typing import Any
from django.core.management.base import BaseCommand, CommandError
from users.models import User

class Command(BaseCommand):
    help = "Disables the active field for given users"

    def add_arguments(self, parser):
        parser.add_argument("user_ids", nargs="+", type=int)
        
    def handle(self, *args, **options):
        for user_id in options["user_ids"]:
            try:
                user = User.objects.get(pk = user_id)
            except User.DoesNotExist:
                raise CommandError('User %s does not exist' % user)
            
            user.is_active = False
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS('Successfully deleted user %s' % user)
            )