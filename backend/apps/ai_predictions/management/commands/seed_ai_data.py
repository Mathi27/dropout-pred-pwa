from django.core.management.base import BaseCommand

from apps.ai_predictions.services.dataset import generate_synthetic_data


class Command(BaseCommand):
    help = "Seed synthetic AI dataset for dropout prediction."

    def add_arguments(self, parser):
        parser.add_argument("--patients", type=int, default=1200)
        parser.add_argument("--doctors", type=int, default=12)
        parser.add_argument("--seed", type=int, default=42)

    def handle(self, *args, **options):
        summary = generate_synthetic_data(
            num_patients=options["patients"],
            num_doctors=options["doctors"],
            seed=options["seed"],
        )
        self.stdout.write(self.style.SUCCESS("Synthetic AI dataset generated."))
        for key, value in summary.items():
            self.stdout.write(f"- {key}: {value}")
