from django import template
from django.template.defaultfilters import stringfilter
import cloudinary.utils

register = template.Library()

@register.filter(name='cloudinary_transform')
def cloudinary_transform(value, transformations):
    """
    Apply Cloudinary transformations to a URL
    
    Usage: {{ image.url|cloudinary_transform:"w=400,h=300,c=fill" }}
    Or: {{ image.url|cloudinary_transform:"w=800,h=600,c=fill,q=auto" }}
    """
    if not value:
        return value
    
    # Parse transformations from string
    if isinstance(transformations, str):
        # Convert string like "w=400,h=300,c=fill" to dict
        transform_dict = {}
        for part in transformations.split(','):
            if '=' in part:
                key, val = part.split('=', 1)
                transform_dict[key.strip()] = val.strip()
        transformations = transform_dict
    
    if not transformations:
        return value
    
    # If it's a Cloudinary URL, apply transformations
    if 'cloudinary.com' in str(value):
        try:
            # Extract public_id from URL
            url = str(value)
            parts = url.split('/')
            for i, part in enumerate(parts):
                if part == 'upload' or part == 'video' or part == 'raw':
                    public_id = '/'.join(parts[i+2:])
                    if '.' in public_id:
                        public_id = public_id.split('.')[0]
                    break
            else:
                return value
            
            # Generate transformed URL
            result = cloudinary.utils.cloudinary_url(
                public_id,
                **transformations
            )
            return result[0]
        except Exception:
            return value
    
    return value

@register.simple_tag
def cloudinary_upload_url(public_id, transformations=None, resource_type='image'):
    """Generate a Cloudinary upload URL"""
    if not public_id:
        return ''
    
    try:
        result = cloudinary.utils.cloudinary_url(
            public_id,
            **transformations
        )
        return result[0]
    except Exception:
        return ''

@register.filter(name='cloudinary_responsive')
def cloudinary_responsive(value, sizes='400,800,1200'):
    """
    Generate responsive image srcset
    
    Usage: {{ image.url|cloudinary_responsive:"400,800,1200" }}
    """
    if not value:
        return value
    
    if 'cloudinary.com' in str(value):
        try:
            url = str(value)
            # Extract public_id
            parts = url.split('/')
            for i, part in enumerate(parts):
                if part == 'upload':
                    public_id = '/'.join(parts[i+2:])
                    if '.' in public_id:
                        public_id = public_id.split('.')[0]
                    break
            else:
                return value
            
            # Generate srcset
            sizes_list = [int(s.strip()) for s in sizes.split(',') if s.strip().isdigit()]
            srcset_parts = []
            for size in sizes_list:
                transformed = cloudinary.utils.cloudinary_url(
                    public_id,
                    width=size,
                    crop='scale'
                )[0]
                srcset_parts.append(f"{transformed} {size}w")
            
            return ', '.join(srcset_parts)
        except Exception:
            return value
    
    return value