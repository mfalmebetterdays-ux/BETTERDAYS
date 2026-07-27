import json
import logging
import os
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache

# Cloudinary imports
import cloudinary
import cloudinary.uploader
import cloudinary.api

from .models import (
    SiteSettings, HeroImage, AboutSection, Service,
    ImpactResult, GalleryImage, Testimonial,
    NewsletterContent, ContactSubmission, NewsletterSubscription,
    FormSubmission, SystemLog, FreeEbook,
    BlogPost, ExpressionsImage, ExpressionsVideo
)

logger = logging.getLogger(__name__)

# ================================================================
# LOGGING HELPER
# ================================================================

def log_system_action(message, level='info', source='views', request=None, data=None):
    """Helper to log system actions with optional data"""
    try:
        log_data = {
            'log_level': level,
            'message': message,
            'source': source,
            'user_ip': request.META.get('REMOTE_ADDR', '') if request else '',
            'user_agent': request.META.get('HTTP_USER_AGENT', '') if request else ''
        }
        
        if data:
            log_data['message'] = f"{message} | Data: {json.dumps(data, default=str)[:500]}"
        
        SystemLog.objects.create(**log_data)
    except Exception as e:
        logger.error(f"Failed to log action: {e}")

# ================================================================
# CLOUDINARY HELPER FUNCTIONS
# ================================================================

def upload_to_cloudinary(file_obj, folder='general', public_id=None, options=None):
    """
    Upload a file to Cloudinary with error handling
    
    Args:
        file_obj: The file object to upload
        folder: The folder to store the file in
        public_id: Optional custom public ID
        options: Additional Cloudinary upload options
    
    Returns:
        dict: Response from Cloudinary with secure_url, public_id, etc.
    """
    try:
        upload_options = {
            'folder': folder,
            'use_filename': True,
            'unique_filename': True,
            'overwrite': False,
            'resource_type': 'auto',
        }
        
        if public_id:
            upload_options['public_id'] = public_id
        
        if options:
            upload_options.update(options)
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(file_obj, **upload_options)
        
        logger.info(f"Successfully uploaded to Cloudinary: {result.get('secure_url')}")
        return result
        
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {str(e)}")
        raise

def delete_from_cloudinary(public_id, resource_type='image'):
    """
    Delete a file from Cloudinary
    
    Args:
        public_id: The public ID of the file
        resource_type: 'image', 'video', or 'raw'
    
    Returns:
        dict: Response from Cloudinary
    """
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        logger.info(f"Deleted from Cloudinary: {public_id}")
        return result
    except Exception as e:
        logger.error(f"Cloudinary delete failed: {str(e)}")
        raise

def get_cloudinary_transformations(file_url, transformations):
    """
    Get a Cloudinary URL with transformations applied
    
    Args:
        file_url: The Cloudinary URL or field
        transformations: Dict of transformations
    
    Returns:
        str: Transformed URL or original URL if failed
    """
    if not file_url:
        return None
    
    url = str(file_url)
    
    # Check if it's a Cloudinary URL
    if 'cloudinary.com' not in url:
        return url
    
    try:
        # Extract public_id from URL
        parts = url.split('/')
        public_id = None
        
        for i, part in enumerate(parts):
            if part in ['upload', 'video', 'raw']:
                # Get the part after upload/version
                public_parts = parts[i+1:]
                # Remove version if present (starts with v)
                if public_parts and public_parts[0].startswith('v'):
                    public_parts = public_parts[1:]
                public_id = '/'.join(public_parts)
                if '.' in public_id:
                    public_id = public_id.split('.')[0]
                break
        
        if not public_id:
            return url
        
        # Generate transformed URL
        result = cloudinary.utils.cloudinary_url(
            public_id,
            **transformations
        )
        return result[0]
        
    except Exception as e:
        logger.error(f"Failed to generate transformed URL: {str(e)}")
        return url

# ================================================================
# MAIN HOME VIEW WITH CACHING
# ================================================================

def home(request):
    """Main home view with Cloudinary integration and caching"""
    try:
        print("\n" + "="*80)
        print(f"[DEBUG] Home view called at: {timezone.now()}")
        
        # Try to get from cache first (5 minute cache)
        cache_key = 'home_page_data'
        cached_data = cache.get(cache_key)
        
        if cached_data and not request.GET.get('refresh'):
            print("[CACHE] Using cached home page data")
            context = cached_data
        else:
            print("[CACHE] Building fresh home page data")
            
            # Get or create site settings
            site_settings = SiteSettings.objects.first()
            if not site_settings:
                print("[WARNING] No SiteSettings found, creating default...")
                site_settings = SiteSettings.objects.create(
                    site_name='Fusion Force LLC',
                    contact_email='info@fusionforce.com',
                    contact_phone='+1 (443) 545-4565'
                )
            
            # Get all dynamic content - OPTIMIZED
            hero_images = HeroImage.objects.filter(is_active=True).order_by('order')[:1]  # Only first hero
            about_section = AboutSection.objects.filter(is_active=True).first()
            services = Service.objects.filter(is_active=True).order_by('order')
            results = ImpactResult.objects.filter(is_active=True).order_by('order')
            
            # GALLERY: Only get first 6 images
            all_gallery_images = GalleryImage.objects.filter(is_active=True).order_by('order')
            gallery_images = all_gallery_images[:6]
            total_gallery_count = all_gallery_images.count()
            has_more_gallery = total_gallery_count > 6
            
            testimonials = Testimonial.objects.filter(is_active=True).order_by('order')[:12]
            newsletter = NewsletterContent.objects.filter(is_active=True).first()
            free_ebook = FreeEbook.objects.filter(is_active=True).first()
            blog_posts = BlogPost.objects.filter(is_active=True).order_by('order', '-created_at')[:3]
            expressions_images = ExpressionsImage.objects.filter(is_active=True).order_by('order')[:10]
            expressions_videos = ExpressionsVideo.objects.filter(is_active=True).order_by('order')[:6]
            
            # Prepare context
            context = {
                'site_settings': site_settings,
                'hero_images': hero_images,
                'about_section': about_section,
                'services': services,
                'results': results,
                'gallery_images': gallery_images,
                'total_gallery_count': total_gallery_count,
                'has_more_gallery': has_more_gallery,
                'testimonials': testimonials,
                'newsletter': newsletter,
                'free_ebook': free_ebook,
                'blog_posts': blog_posts,
                'expressions_images': expressions_images,
                'expressions_videos': expressions_videos,
                'cloudinary_cloud_name': settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'),
                'is_debug': settings.DEBUG,
            }
            
            # Cache for 5 minutes
            cache.set(cache_key, context, 300)
        
        # Check for subscription confirmation
        if 'subscribed' in request.GET:
            context['subscribed'] = True
        
        # Log page view (random sampling to reduce DB load)
        import random
        if random.randint(1, 100) == 1:
            log_system_action(
                f"Home page viewed from IP: {request.META.get('REMOTE_ADDR', 'Unknown')}",
                level='info',
                source='home_view',
                request=request
            )
        
        # Render response
        response = render(request, 'main/index.html', context)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        response['X-Frame-Options'] = 'DENY'
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        
        return response
        
    except Exception as e:
        print(f"[ERROR] in home view: {str(e)}")
        import traceback
        traceback.print_exc()
        
        log_system_action(
            f"Home view error: {str(e)}",
            level='error',
            source='home_view',
            request=request
        )
        
        context = {
            'site_settings': SiteSettings.objects.first() or SiteSettings(),
            'error': True,
            'error_message': str(e) if settings.DEBUG else None,
            'cloudinary_cloud_name': settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'),
        }
        
        return render(request, 'main/index.html', context)

# ================================================================
# GALLERY API - FOR LAZY LOADING
# ================================================================

@require_GET
def get_gallery_images(request):
    """
    API endpoint for lazy loading gallery images
    Returns 3 images at a time
    """
    try:
        page = int(request.GET.get('page', 1))
        per_page = 3  # Load 3 at a time
        
        images = GalleryImage.objects.filter(is_active=True).order_by('order')
        paginator = Paginator(images, per_page)
        page_obj = paginator.get_page(page)
        
        data = {
            'images': [
                {
                    'id': img.id,
                    'title': img.title,
                    'url': img.image.url,
                    'description': img.description,
                    'position': img.position,
                }
                for img in page_obj
            ],
            'has_next': page_obj.has_next(),
            'next_page': page + 1 if page_obj.has_next() else None,
            'total': paginator.count,
            'loaded': page * per_page,
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Gallery API error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# ================================================================
# MEDIA PAGE VIEW
# ================================================================

def media_page(request):
    """Media and Press page with Cloudinary integration"""
    try:
        # Get media-related content
        gallery_images = GalleryImage.objects.filter(is_active=True).order_by('order')
        expressions_images = ExpressionsImage.objects.filter(is_active=True).order_by('order')
        expressions_videos = ExpressionsVideo.objects.filter(is_active=True).order_by('order')
        
        # Pagination for gallery
        paginator = Paginator(gallery_images, 12)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context = {
            'gallery_images': page_obj,
            'expressions_images': expressions_images,
            'expressions_videos': expressions_videos,
            'cloudinary_cloud_name': settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'),
            'site_settings': SiteSettings.objects.first(),
        }
        
        log_system_action(
            f"Media page viewed from IP: {request.META.get('REMOTE_ADDR', 'Unknown')}",
            level='info',
            source='media_page',
            request=request
        )
        
        return render(request, 'main/media.html', context)
        
    except Exception as e:
        logger.error(f"Media page error: {str(e)}")
        log_system_action(
            f"Media page error: {str(e)}",
            level='error',
            source='media_page',
            request=request
        )
        
        context = {
            'error': True,
            'error_message': str(e) if settings.DEBUG else None,
            'site_settings': SiteSettings.objects.first(),
        }
        return render(request, 'main/media.html', context)

# ================================================================
# CONTACT FORM SUBMISSION
# ================================================================

@csrf_exempt
@require_POST
def contact_submit(request):
    """Handle contact form submission with Cloudinary file support"""
    try:
        # Check if it's JSON or form data
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body)
        else:
            data = request.POST.dict()
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'organization', 'event_type', 'event_details']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'status': 'error',
                    'message': f'{field.replace("_", " ").title()} is required.'
                }, status=400)
        
        # Handle file uploads if any
        uploaded_files = []
        if request.FILES:
            for file_key, file_obj in request.FILES.items():
                try:
                    result = upload_to_cloudinary(
                        file_obj,
                        folder='contact_submissions',
                        options={'resource_type': 'auto'}
                    )
                    uploaded_files.append({
                        'field': file_key,
                        'url': result.get('secure_url'),
                        'public_id': result.get('public_id')
                    })
                except Exception as e:
                    logger.error(f"File upload failed for {file_key}: {str(e)}")
        
        # Create submission
        submission = ContactSubmission.objects.create(
            full_name=data['full_name'],
            email=data['email'],
            organization=data['organization'],
            event_type=data['event_type'],
            event_details=data['event_details']
        )
        
        # Add uploaded files info to notes if any
        if uploaded_files:
            notes = f"Uploaded files: {json.dumps(uploaded_files, default=str)}"
            submission.notes = notes
            submission.save()
        
        log_system_action(
            f"New contact submission from {submission.full_name} ({submission.organization})",
            level='success',
            source='contact_form',
            request=request,
            data={'submission_id': submission.id, 'files': len(uploaded_files)}
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Thank you for your booking request! Pamela will review your details and get back to you within 24 hours.',
            'submission_id': submission.id,
            'files_uploaded': len(uploaded_files)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request data.'
        }, status=400)
    except Exception as e:
        logger.error(f"Contact submission error: {str(e)}")
        log_system_action(
            f"Contact submission error: {str(e)}",
            level='error',
            source='contact_form',
            request=request
        )
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred. Please try again later.'
        }, status=500)

# ================================================================
# NEWSLETTER SUBSCRIPTION
# ================================================================

@csrf_exempt
@require_POST
def newsletter_submit(request):
    """Handle newsletter subscription with optional file attachments"""
    try:
        # Check if it's JSON or form data
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body)
        else:
            data = request.POST.dict()
        
        email = data.get('email', '').strip()
        name = data.get('name', '').strip()
        source = data.get('source', 'newsletter_section')
        agreed_to_terms = data.get('agreed_to_terms', True)
        
        if not email:
            return JsonResponse({
                'status': 'error',
                'message': 'Email is required.'
            }, status=400)
        
        # Check for existing subscription
        if NewsletterSubscription.objects.filter(email=email).exists():
            subscription = NewsletterSubscription.objects.get(email=email)
            return JsonResponse({
                'status': 'info',
                'message': f'You are already subscribed to our newsletter! (Subscribed on {subscription.created_at.strftime("%Y-%m-%d")})'
            })
        
        # Create new subscription
        subscription = NewsletterSubscription.objects.create(
            email=email,
            name=name if name else email.split('@')[0],
            source=source,
            agreed_to_terms=agreed_to_terms,
            is_active=True
        )
        
        # Handle any file uploads
        if request.FILES:
            for file_key, file_obj in request.FILES.items():
                try:
                    upload_to_cloudinary(
                        file_obj,
                        folder=f'newsletter_subscriptions/{subscription.id}',
                        options={'resource_type': 'auto'}
                    )
                except Exception as e:
                    logger.error(f"File upload failed for {file_key}: {str(e)}")
        
        log_system_action(
            f"New newsletter subscription: {email}",
            level='success',
            source='newsletter_form',
            request=request,
            data={'subscription_id': subscription.id, 'source': source}
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Thank you for subscribing to our newsletter!',
            'subscription_id': subscription.id
        })
        
    except IntegrityError:
        return JsonResponse({
            'status': 'info',
            'message': 'You are already subscribed to our newsletter!'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request data.'
        }, status=400)
    except Exception as e:
        logger.error(f"Newsletter subscription error: {str(e)}")
        log_system_action(
            f"Newsletter subscription error: {str(e)}",
            level='error',
            source='newsletter_form',
            request=request
        )
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred. Please try again later.'
        }, status=500)

# ================================================================
# FORMSUBMIT WEBHOOK
# ================================================================

@csrf_exempt
@require_POST
def form_submit_webhook(request):
    """Webhook to receive form submissions from FormSubmit"""
    try:
        # Get the raw data
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body)
        else:
            data = request.POST.dict()
        
        # Log the webhook receipt
        log_system_action(
            f"FormSubmit webhook received: {data.get('_subject', 'Unknown')}",
            level='info',
            source='formsubmit_webhook',
            request=request,
            data=data
        )
        
        # Store the submission
        FormSubmission.objects.create(
            source=data.get('source', 'unknown'),
            form_data=data,
            processed=False
        )
        
        # Handle any file uploads in the webhook
        if request.FILES:
            for file_key, file_obj in request.FILES.items():
                try:
                    upload_to_cloudinary(
                        file_obj,
                        folder='webhook_uploads',
                        options={'resource_type': 'auto'}
                    )
                except Exception as e:
                    logger.error(f"Webhook file upload failed: {str(e)}")
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        logger.error(f"FormSubmit webhook error: {str(e)}")
        log_system_action(
            f"FormSubmit webhook error: {str(e)}",
            level='error',
            source='formsubmit_webhook',
            request=request
        )
        return JsonResponse({'status': 'error'}, status=500)

# ================================================================
# EBOOK DOWNLOAD
# ================================================================

@require_POST
def download_ebook(request, ebook_id):
    """Handle ebook download and increment count with Cloudinary"""
    try:
        ebook = get_object_or_404(FreeEbook, id=ebook_id, is_active=True)
        
        # Increment download count
        ebook.increment_download_count()
        
        # Get the file URL
        file_url = ebook.ebook_file.url if ebook.ebook_file else None
        
        if not file_url:
            return JsonResponse({
                'status': 'error',
                'message': 'Ebook file not available.'
            }, status=404)
        
        log_system_action(
            f"Ebook download: {ebook.title} by {request.META.get('REMOTE_ADDR', 'Unknown')}",
            level='info',
            source='ebook_download',
            request=request,
            data={'ebook_id': ebook_id, 'download_count': ebook.download_count}
        )
        
        return JsonResponse({
            'status': 'success',
            'download_url': file_url,
            'title': ebook.title,
            'download_count': ebook.download_count
        })
        
    except FreeEbook.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Ebook not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Ebook download error: {str(e)}")
        log_system_action(
            f"Ebook download error: {str(e)}",
            level='error',
            source='ebook_download',
            request=request
        )
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred'
        }, status=500)

# ================================================================
# CLOUDINARY UPLOAD ENDPOINT (For admin/AJAX uploads)
# ================================================================

@csrf_exempt
@require_POST
def cloudinary_upload_endpoint(request):
    """
    AJAX endpoint for uploading files directly to Cloudinary
    Requires authentication
    """
    try:
        # Check if user is authenticated (for admin use)
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required'
            }, status=401)
        
        if not request.FILES:
            return JsonResponse({
                'status': 'error',
                'message': 'No file provided'
            }, status=400)
        
        file_obj = request.FILES.get('file')
        if not file_obj:
            return JsonResponse({
                'status': 'error',
                'message': 'No file uploaded'
            }, status=400)
        
        folder = request.POST.get('folder', 'uploads')
        public_id = request.POST.get('public_id', None)
        
        # Upload to Cloudinary
        result = upload_to_cloudinary(
            file_obj,
            folder=folder,
            public_id=public_id,
            options={'resource_type': 'auto'}
        )
        
        log_system_action(
            f"File uploaded via AJAX: {result.get('public_id')}",
            level='success',
            source='cloudinary_upload',
            request=request,
            data={'folder': folder, 'size': file_obj.size}
        )
        
        return JsonResponse({
            'status': 'success',
            'url': result.get('secure_url'),
            'public_id': result.get('public_id'),
            'format': result.get('format'),
            'width': result.get('width'),
            'height': result.get('height'),
            'bytes': result.get('bytes'),
        })
        
    except Exception as e:
        logger.error(f"Cloudinary upload endpoint error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# ================================================================
# CLOUDINARY DELETE ENDPOINT (For admin use)
# ================================================================

@csrf_exempt
@require_POST
def cloudinary_delete_endpoint(request):
    """
    AJAX endpoint for deleting files from Cloudinary
    Requires authentication
    """
    try:
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required'
            }, status=401)
        
        data = json.loads(request.body)
        public_id = data.get('public_id')
        resource_type = data.get('resource_type', 'image')
        
        if not public_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Public ID required'
            }, status=400)
        
        # Delete from Cloudinary
        result = delete_from_cloudinary(public_id, resource_type)
        
        log_system_action(
            f"File deleted from Cloudinary: {public_id}",
            level='info',
            source='cloudinary_delete',
            request=request
        )
        
        return JsonResponse({
            'status': 'success',
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Cloudinary delete endpoint error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# ================================================================
# GET OPTIMIZED IMAGE URL
# ================================================================

@require_GET
def get_optimized_image(request):
    """
    Get an optimized image URL with transformations
    Usage: /api/get-optimized-image/?url=https://res.cloudinary.com/...
    """
    try:
        url = request.GET.get('url')
        if not url:
            return JsonResponse({
                'status': 'error',
                'message': 'URL parameter required'
            }, status=400)
        
        # Parse transformations from query params
        transformations = {}
        for param in ['width', 'height', 'crop', 'quality', 'format', 'gravity']:
            value = request.GET.get(param)
            if value:
                transformations[param] = value
        
        # Apply transformations
        optimized_url = get_cloudinary_transformations(url, transformations)
        
        return JsonResponse({
            'status': 'success',
            'original_url': url,
            'optimized_url': optimized_url,
            'transformations': transformations
        })
        
    except Exception as e:
        logger.error(f"Get optimized image error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# ================================================================
# HEALTH CHECK (For monitoring)
# ================================================================

def health_check(request):
    """
    Health check endpoint for monitoring
    """
    try:
        # Check database connection
        SiteSettings.objects.exists()
        
        # Check Cloudinary connection
        cloudinary.api.ping()
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'cloudinary': 'connected',
            'database': 'connected'
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=500)

# ================================================================
# TEMPLATE CONTEXT PROCESSOR
# ================================================================

def cloudinary_context(request):
    """
    Context processor to add Cloudinary config to all templates
    Add to TEMPLATES context_processors in settings.py:
    
    'main.views.cloudinary_context'
    """
    return {
        'CLOUDINARY_CLOUD_NAME': settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'),
        'CLOUDINARY_API_KEY': settings.CLOUDINARY_STORAGE.get('API_KEY'),
        'CLOUDINARY_SECURE': True,
        'CLOUDINARY_TRANSFORMATIONS': {
            'default': {'quality': 'auto', 'fetch_format': 'auto'},
            'thumbnail': {'width': 150, 'height': 150, 'crop': 'fill', 'gravity': 'face'},
            'medium': {'width': 400, 'height': 300, 'crop': 'fill'},
            'large': {'width': 800, 'height': 600, 'crop': 'fill'},
            'hero': {'width': 1200, 'height': 800, 'crop': 'fill', 'quality': 'auto'},
        }
    }