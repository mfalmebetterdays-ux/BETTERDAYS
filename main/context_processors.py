from django.conf import settings

def cloudinary_config(request):
    """Add Cloudinary config to template context"""
    return {
        'CLOUDINARY_CLOUD_NAME': settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'),
        'CLOUDINARY_API_KEY': settings.CLOUDINARY_STORAGE.get('API_KEY'),
        'CLOUDINARY_SECURE': True,
    }