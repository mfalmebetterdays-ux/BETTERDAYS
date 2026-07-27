from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from main.views import (
    home, 
    media_page, 
    contact_submit, 
    newsletter_submit, 
    form_submit_webhook, 
    download_ebook,
    get_gallery_images,
    cloudinary_upload_endpoint,
    cloudinary_delete_endpoint,
    get_optimized_image,
    health_check
)

urlpatterns = [
    # Main pages
    path('', home, name='home'),
    path('media/', media_page, name='media_page'),
    
    # API endpoints
    path('api/contact-submit/', contact_submit, name='contact_submit'),
    path('api/newsletter-submit/', newsletter_submit, name='newsletter_submit'),
    path('api/formsubmit-webhook/', form_submit_webhook, name='formsubmit_webhook'),
    path('api/download-ebook/<int:ebook_id>/', download_ebook, name='download_ebook'),
    
    # Gallery API - For lazy loading
    path('api/gallery-images/', get_gallery_images, name='gallery_api'),
    
    # Cloudinary API endpoints
    path('api/cloudinary-upload/', cloudinary_upload_endpoint, name='cloudinary_upload'),
    path('api/cloudinary-delete/', cloudinary_delete_endpoint, name='cloudinary_delete'),
    path('api/get-optimized-image/', get_optimized_image, name='get_optimized_image'),
    
    # Health check
    path('health/', health_check, name='health_check'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)