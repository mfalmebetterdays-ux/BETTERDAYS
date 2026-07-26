from django.core.management.base import BaseCommand
from main.cloudinary_utils import batch_migrate_to_cloudinary

class Command(BaseCommand):
    help = 'Migrate all media files to Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
            self.stdout.write('Would migrate the following models:')
            self.stdout.write('  - HeroImage.image')
            self.stdout.write('  - AboutSection.image, image_2')
            self.stdout.write('  - GalleryImage.image')
            self.stdout.write('  - Testimonial.avatar')
            self.stdout.write('  - NewsletterContent.image, pdf_file')
            self.stdout.write('  - BlogPost.image')
            self.stdout.write('  - ExpressionsImage.image')
            self.stdout.write('  - ExpressionsVideo.video_file')
            self.stdout.write('  - FreeEbook.ebook_file, cover_image')
            self.stdout.write('  - SiteSettings.logo')
            return
        
        self.stdout.write(self.style.NOTICE('Starting migration to Cloudinary...'))
        self.stdout.write('This may take a while depending on the number of files.')
        
        try:
            migrated, failed = batch_migrate_to_cloudinary()
            
            if migrated > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Successfully migrated {migrated} files to Cloudinary')
                )
            
            if failed > 0:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to migrate {failed} files')
                )
            
            if migrated == 0 and failed == 0:
                self.stdout.write(
                    self.style.WARNING('No files found to migrate')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Migration failed: {str(e)}')
            )
            raise