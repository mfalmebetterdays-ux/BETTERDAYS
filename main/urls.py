# main/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Import views directly (not from . import views which might cause circular import)
from main.views import home, contact_submit, newsletter_submit, form_submit_webhook, download_ebook

urlpatterns = [
    path('', home, name='home'),
    path('api/contact-submit/', contact_submit, name='contact_submit'),
    path('api/newsletter-submit/', newsletter_submit, name='newsletter_submit'),
    path('api/formsubmit-webhook/', form_submit_webhook, name='formsubmit_webhook'),
    path('api/download-ebook/<int:ebook_id>/', download_ebook, name='download_ebook'),
]

# Only add media serving if MEDIA_ROOT is set and not empty
if settings.MEDIA_ROOT:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)