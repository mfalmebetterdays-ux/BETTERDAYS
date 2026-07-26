from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from main.views import home, contact_submit, newsletter_submit, form_submit_webhook, download_ebook, media_page

urlpatterns = [
    path('', home, name='home'),
    path('api/contact-submit/', contact_submit, name='contact_submit'),
    path('api/newsletter-submit/', newsletter_submit, name='newsletter_submit'),
    path('api/formsubmit-webhook/', form_submit_webhook, name='formsubmit_webhook'),
    path('api/download-ebook/<int:ebook_id>/', download_ebook, name='download_ebook'),
    path('media/', media_page, name='media_page'),
]

# Optional: Serve media locally in development (will be overridden by Cloudinary)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)