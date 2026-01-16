# main/templatetags/cloudinary_fix.py
from django import template

register = template.Library()

@register.filter
def fix_cloudinary_url(url):
    """
    Fix Cloudinary URLs that are missing the colon after https
    Example: https:/res.cloudinary.com/... -> https://res.cloudinary.com/...
    """
    if not url:
        return ''
    
    # Fix the broken https:/ issue
    if url.startswith('https:/') and not url.startswith('https://'):
        url = url.replace('https:/', 'https://', 1)
    
    # Ensure it's a full Cloudinary URL
    if url and not url.startswith('https://res.cloudinary.com/'):
        cloud_name = 'drq16etks'  # Your Cloudinary cloud name
        if url.startswith('/'):
            url = url[1:]
        url = f'https://res.cloudinary.com/{cloud_name}/{url}'
    
    # For images, ensure proper transformation path
    if url and '/image/' in url:
        if '/image/upload/' not in url:
            url = url.replace('/image/', '/image/upload/', 1)
        # Add default image format if missing extension
        if '.' not in url.split('/')[-1]:
            url = f'{url}.jpg'
    
    return url

@register.filter
def is_cloudinary_url(url):
    """Check if URL is a Cloudinary URL"""
    return url and 'cloudinary.com' in url