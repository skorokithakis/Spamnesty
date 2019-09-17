from django.core.management.base import BaseCommand
from main.models import Message


class Command(BaseCommand):
    help = "Send unsent messages that should now be sent."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            help="Check, but do not send any email.",
            default=False,
        )

    def handle(self, *args, **options):
        if options["dry_run"]:
            self.stdout.write(
                "%d messages would have been sent." % Message.objects.unsent().count()
            )
            return
        sent_count = Message.send_unsent()
        self.stdout.write("%d messages were sent." % sent_count)
