"""
Management command to seed demo data for DentalAI.
Run with: python manage.py seed_demo_data
"""

from django.core.management.base import BaseCommand
from django.core import management

class Command(BaseCommand):
    help = 'Seed demo data for DentalAI platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Flush existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write(self.style.WARNING('Flushing existing data...'))
            management.call_command('flush', '--noinput')
            self.stdout.write(self.style.SUCCESS('✓ Database flushed'))
        
        # Import and run the seed script
        import sys
        from pathlib import Path
        
        # Add backend directory to path
        backend_dir = Path(__file__).parent.parent.parent.parent.parent
        seed_script = backend_dir / 'seed_demo_data_v2.py'
        
        if not seed_script.exists():
            self.stdout.write(self.style.ERROR(f'Seed script not found: {seed_script}'))
            return
        
        # Execute the seed script
        self.stdout.write(self.style.SUCCESS('🚀 Starting demo data seeding...'))
        
        # Read and execute the script
        with open(seed_script, 'r') as f:
            script_content = f.read()
        
        # Execute in the current namespace
        exec(script_content, {
            '__name__': '__main__',
            '__file__': str(seed_script),
        })
        
        self.stdout.write(self.style.SUCCESS('\n✅ Demo data seeding completed!'))