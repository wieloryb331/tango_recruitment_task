from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from calendar_app.models import Company


class Command(BaseCommand):
    help = "Adds user with given username, password and company_id"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="User username")
        parser.add_argument("password", type=str, help="User password")
        parser.add_argument("company_id", type=str, help="User company_id")

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        company_id = options["company_id"]

        company, _ = Company.objects.get_or_create(id=company_id)

        user_model = get_user_model()
        user_model.objects.create_user(
            username=username,
            password=password,
            company=company
        )
        self.stdout.write(self.style.SUCCESS('Successfully created user "%s"' % username))