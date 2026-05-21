from django.core.management.base import BaseCommand

from apps.ai_predictions.services.training import train_models


class Command(BaseCommand):
    help = "Train dropout prediction models and store artifacts."

    def add_arguments(self, parser):
        parser.add_argument("--no-activate", action="store_true", help="Do not set best model active")

    def handle(self, *args, **options):
        versions = train_models(set_active=not options["no_activate"])
        self.stdout.write(self.style.SUCCESS("Training completed."))
        for version in versions:
            metrics = version.metrics or {}
            self.stdout.write(
                f"- {version.model_type}: AUC {metrics.get('auc', 0):.3f}"
            )
