from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.safestring import mark_safe
import json
import csv
from datetime import timedelta

from .models import (
    SiteSettings, HeroImage, AboutSection, Service,
    ImpactResult, GalleryImage, Testimonial,
    NewsletterContent, ContactSubmission, NewsletterSubscription,
    FormSubmission, SystemLog, FreeEbook
)

# ============ ADMIN SITE CONFIG ============
admin.site.site_header = "FUSION-FORCE LLC ADMIN"
admin.site.site_title = "Fusion Force Administration"
admin.site.index_title = "Welcome to Fusion Force Dashboard"

# ============ CUSTOM ADMIN ACTIONS ============
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)
    messages.success(request, f"{queryset.count()} items marked as active")
make_active.short_description = "✅ Mark selected as active"

def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)
    messages.success(request, f"{queryset.count()} items marked as inactive")
make_inactive.short_description = "❌ Mark selected as inactive"

def duplicate_items(modeladmin, request, queryset):
    for obj in queryset:
        obj.pk = None
        obj.title = f"{obj.title} (Copy)"
        obj.save()
    messages.success(request, f"{queryset.count()} items duplicated")
duplicate_items.short_description = "📋 Duplicate selected items"

def export_as_json(modeladmin, request, queryset):
    data = []
    for obj in queryset:
        data.append({
            'id': obj.id,
            'title': str(obj),
            'created': obj.created_at.isoformat() if hasattr(obj, 'created_at') else None
        })
    response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="export.json"'
    return response
export_as_json.short_description = "📤 Export selected as JSON"

# ============ CUSTOM ADMIN FILTERS ============
class ActiveFilter(admin.SimpleListFilter):
    title = 'Active Status'
    parameter_name = 'is_active'
    
    def lookups(self, request, model_admin):
        return (
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True)
        if self.value() == 'inactive':
            return queryset.filter(is_active=False)

# ============ SITE SETTINGS ADMIN ============
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'logo_preview', 'contact_email', 'contact_phone', 'updated_at_display']
    list_display_links = ['site_name']
    readonly_fields = ['created_at', 'updated_at', 'logo_preview_large']
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: contain; background: #f0f0f0; padding: 5px; border-radius: 5px;" />', 
                obj.logo.url
            )
        return format_html('<div style="width: 50px; height: 50px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 5px;">No Logo</div>')
    logo_preview.short_description = 'Logo'
    
    def logo_preview_large(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; object-fit: contain; background: #f0f0f0; padding: 10px; border-radius: 10px; border: 1px solid #ddd;" />', 
                obj.logo.url
            )
        return "No logo uploaded"
    logo_preview_large.short_description = 'Logo Preview'
    
    def updated_at_display(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')
    updated_at_display.short_description = 'Last Updated'
    
    fieldsets = (
        ('Site Information', {
            'fields': ('site_name', 'logo', 'logo_preview_large'),
            'classes': ('wide',)
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse', 'wide')
        }),
    )
    
    def has_add_permission(self, request):
        return SiteSettings.objects.count() == 0

# ============ HERO IMAGE ADMIN ============
@admin.register(HeroImage)
class HeroImageAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'position_display', 'order', 'is_active_badge', 'created_at_display']
    list_filter = ['position', ActiveFilter, 'created_at']
    list_editable = ['order']
    list_display_links = ['title']
    search_fields = ['title']
    actions = [make_active, make_inactive, duplicate_items]
    readonly_fields = ['created_at', 'image_preview_large']
    list_per_page = 20
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />', 
                obj.image.url
            )
        return format_html('<div style="width: 60px; height: 40px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 4px;">No Image</div>')
    image_preview.short_description = 'Preview'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 300px; object-fit: contain; border-radius: 8px; border: 2px solid #ddd;" />', 
                obj.image.url
            )
        return "No image uploaded"
    image_preview_large.short_description = 'Large Preview'
    
    def position_display(self, obj):
        color = 'blue' if obj.position == 'desktop' else 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_position_display()
        )
    position_display.short_description = 'Position'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Active</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_display.short_description = 'Created'
    
    fieldsets = (
        ('Hero Image Details', {
            'fields': ('title', 'image', 'image_preview_large', 'position'),
            'classes': ('wide',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
            'classes': ('wide',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse', 'wide')
        }),
    )

# ============ ABOUT SECTION ADMIN ============
@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'is_active_badge', 'created_at_display', 'updated_at_display']
    list_display_links = ['title']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large', 'image_2_preview_large', 'bullet_points_preview', 'content_preview_field']
    actions = [make_active, make_inactive, duplicate_items]
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />', 
                obj.image.url
            )
        return format_html('<div style="width: 50px; height: 50px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 4px;">No Image</div>')
    image_preview.short_description = 'Image'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Active</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_display.short_description = 'Created At'
    
    def updated_at_display(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')
    updated_at_display.short_description = 'Updated At'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 300px; object-fit: contain; border-radius: 8px; border: 2px solid #ddd;" />', 
                obj.image.url
            )
        return "No image uploaded"
    image_preview_large.short_description = 'Image Preview'
    
    def bullet_points_preview(self, obj):
        if obj.bullet_points:
            points = obj.bullet_points.split('\n')
            html = '<div style="background: #f8f9fa; padding: 10px; border-radius: 5px; border: 1px solid #ddd;">'
            html += '<strong>Bullet Points Preview:</strong><ul style="margin: 5px 0 0 20px;">'
            for point in points:
                if point.strip():
                    html += f'<li>{point.strip()}</li>'
            html += '</ul></div>'
            return format_html(html)
        return "No bullet points"
    bullet_points_preview.short_description = 'Bullet Points Preview'
    
    def content_preview_field(self, obj):
        if obj.content:
            preview = obj.content[:150] + '...' if len(obj.content) > 150 else obj.content
            return format_html(
                '<div style="background: #f8f9fa; padding: 10px; border-radius: 5px; border: 1px solid #ddd; max-width: 600px; max-height: 200px; overflow: auto;">{}</div>',
                preview
            )
        return "No content"
    content_preview_field.short_description = 'Content Preview'
    
    def image_2_preview_large(self, obj):
        if obj.image_2:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 300px; object-fit: contain; border-radius: 8px; border: 2px solid #ddd; margin-top: 10px;" />', 
                obj.image_2.url
            )
        return "No second image uploaded"
    image_2_preview_large.short_description = 'Second Image Preview'
    
    fieldsets = (
        ('About Content', {
            'fields': ('title', 'content', 'content_preview_field'),
            'description': 'Format your content with **bold titles** and bullet points (•). Second image appears automatically when you have 3+ sections.',
            'classes': ('wide',)
        }),
        ('Main Image', {
            'fields': ('image', 'image_preview_large'),
            'classes': ('wide',)
        }),
        ('Second Image (Shows when content is long)', {
            'fields': ('image_2', 'image_2_preview_large'),
            'description': 'Upload a second image that will automatically appear when content has 3+ sections.',
            'classes': ('wide',)
        }),
        ('Bullet Points', {
            'fields': ('bullet_points', 'bullet_points_preview'),
            'description': 'Enter each bullet point on a new line. They will appear in the about section.',
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_active',),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse', 'wide')
        }),
    )

# ============ SERVICE ADMIN ============
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['icon_preview', 'title', 'service_type_display', 'button_text', 'order', 'is_active_badge', 'created_at_display']
    list_filter = ['service_type', ActiveFilter, 'created_at']
    list_editable = ['order', 'button_text']
    list_display_links = ['title']
    search_fields = ['title', 'description', 'topics']
    actions = [make_active, make_inactive, duplicate_items]
    readonly_fields = ['created_at', 'updated_at', 'topics_preview']
    list_per_page = 20
    
    def icon_preview(self, obj):
        if obj.icon:
            return format_html(
                '<i class="{} fa-lg" style="color: #053e91;"></i>',
                obj.icon
            )
        return format_html('<div style="width: 30px; height: 30px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 4px;">No Icon</div>')
    icon_preview.short_description = 'Icon'
    
    def service_type_display(self, obj):
        colors = {
            'keynote': '#28a745',
            'training': '#007bff',
            'sales': '#6f42c1'
        }
        color = colors.get(obj.service_type, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color,
            obj.get_service_type_display()
        )
    service_type_display.short_description = 'Type'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Active</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def topics_preview(self, obj):
        if obj.topics_list:
            html = '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6;">'
            html += '<h4 style="margin-top: 0; color: #053e91;">Topics Preview:</h4>'
            for topic in obj.topics_list:
                html += f'<span style="display: inline-block; background: white; color: #053e91; padding: 4px 12px; margin: 3px; border-radius: 20px; border: 1px solid #053e91; font-size: 13px;">{topic}</span> '
            html += '</div>'
            return format_html(html)
        return "No topics defined"
    topics_preview.short_description = 'Topics Preview'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_display.short_description = 'Created'
    
    fieldsets = (
        ('Service Information', {
            'fields': ('title', 'service_type', 'description'),
            'classes': ('wide',)
        }),
        ('Display Settings', {
            'fields': ('icon', 'topics', 'topics_preview', 'button_text'),
            'description': 'For topics, separate with commas. For icon, use Font Awesome classes like "fas fa-microphone"',
            'classes': ('wide',)
        }),
        ('Order & Status', {
            'fields': ('order', 'is_active'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse', 'wide')
        }),
    )

# ============ IMPACT RESULT ADMIN ============
@admin.register(ImpactResult)
class ImpactResultAdmin(admin.ModelAdmin):
    list_display = ['value', 'title', 'order', 'is_active_badge', 'created_at_display']
    list_display_links = ['title']
    list_filter = [ActiveFilter, 'created_at']
    list_editable = ['value', 'order']
    search_fields = ['title', 'value']
    actions = [make_active, make_inactive, duplicate_items]
    readonly_fields = ['created_at']
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Active</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_display.short_description = 'Created'
    
    fieldsets = (
        ('Impact Result', {
            'fields': ('title', 'value'),
            'classes': ('wide',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
            'classes': ('wide',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse', 'wide')
        }),
    )

# ============ GALLERY IMAGE ADMIN ============
@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'position_display', 'order', 'is_active_badge', 'created_at_display']
    list_filter = ['position', ActiveFilter, 'created_at']
    list_editable = ['order']
    list_display_links = ['title']
    search_fields = ['title', 'description']
    actions = [make_active, make_inactive, duplicate_items]
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large']
    list_per_page = 20
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />', 
                obj.image.url
            )
        return format_html('<div style="width: 60px; height: 40px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 4px;">No Image</div>')
    image_preview.short_description = 'Preview'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 300px; object-fit: contain; border-radius: 8px; border: 2px solid #ddd;" />', 
                obj.image.url
            )
        return "No image uploaded"
    image_preview_large.short_description = 'Large Preview'
    
    def position_display(self, obj):
        colors = {
            'large': '#dc3545',
            'small': '#17a2b8',
            'tall': '#28a745'
        }
        color = colors.get(obj.position, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color,
            obj.get_position_display()
        )
    position_display.short_description = 'Position'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Active</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_display.short_description = 'Created'
    
    fieldsets = (
        ('Gallery Image Details', {
            'fields': ('title', 'image', 'image_preview_large', 'description', 'position'),
            'classes': ('wide',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse', 'wide')
        }),
    )

# ============ TESTIMONIAL ADMIN ============
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['avatar_preview', 'client_name', 'company', 'position', 'order', 'is_active_badge', 'created_at_display']
    list_filter = ['is_active', 'company', 'created_at']
    list_editable = ['order']
    list_display_links = ['client_name']
    search_fields = ['client_name', 'company', 'position', 'content']
    actions = [make_active, make_inactive, duplicate_items]
    readonly_fields = ['created_at', 'updated_at', 'avatar_preview_large']
    list_per_page = 20
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 50%; border: 2px solid #053e91;" />', 
                obj.avatar.url
            )
        return format_html(
            '<div style="width: 40px; height: 40px; background: #f0f0f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #053e91; font-weight: bold; font-size: 14px;">{}</div>',
            obj.client_name[:2].upper() if obj.client_name else "??"
        )
    avatar_preview.short_description = 'Avatar'
    
    def avatar_preview_large(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 150px; height: 150px; object-fit: cover; border-radius: 50%; border: 3px solid #053e91;" />', 
                obj.avatar.url
            )
        return format_html(
            '<div style="width: 150px; height: 150px; background: #f0f0f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #053e91; font-weight: bold; font-size: 24px; border: 3px solid #053e91;">{}</div>',
            obj.client_name[:2].upper() if obj.client_name else "??"
        )
    avatar_preview_large.short_description = 'Large Preview'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Active</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_display.short_description = 'Created'
    
    fieldsets = (
        ('Client Information', {
            'fields': ('client_name', 'position', 'company'),
            'classes': ('wide',)
        }),
        ('Testimonial Content', {
            'fields': ('content', 'avatar', 'avatar_preview_large'),
            'description': 'Avatar should be a square image (e.g., 300x300 pixels)',
            'classes': ('wide',)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse', 'wide')
        }),
    )

# ============ NEWSLETTER CONTENT ADMIN ============
@admin.register(NewsletterContent)
class NewsletterContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'pdf_preview', 'is_active_badge', 'created_at_display', 'updated_at_display']
    list_display_links = ['title']
    search_fields = ['title', 'subtitle']
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large', 'benefits_preview', 'pdf_link']
    actions = [make_active, make_inactive]
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />', 
                obj.image.url
            )
        return format_html('<div style="width: 50px; height: 50px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 4px;">No Image</div>')
    image_preview.short_description = 'Image'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 300px; object-fit: contain; border-radius: 8px; border: 2px solid #ddd;" />', 
                obj.image.url
            )
        return "No image uploaded"
    image_preview_large.short_description = 'Large Preview'
    
    def pdf_preview(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank" style="background: #dc3545; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px; text-decoration: none;">📄 View PDF</a>',
                obj.pdf_file.url
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">No PDF</span>'
        )
    pdf_preview.short_description = 'PDF'
    
    def pdf_link(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank" class="button">Open PDF in new tab</a>',
                obj.pdf_file.url
            )
        return "No PDF uploaded"
    pdf_link.short_description = 'PDF Link'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Active</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def benefits_preview(self, obj):
        if obj.benefits_list:
            html = '<div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6;">'
            html += '<h4 style="margin-top: 0; color: #053e91;">Benefits Preview (Two Columns):</h4>'
            html += '<div style="column-count: 2; column-gap: 30px;">'
            for benefit in obj.benefits_list:
                html += f'<div style="margin-bottom: 10px; break-inside: avoid;">'
                html += f'<span style="color: #28a745; margin-right: 8px;">✓</span> {benefit}'
                html += '</div>'
            html += '</div></div>'
            return format_html(html)
        return "No benefits defined"
    benefits_preview.short_description = 'Benefits Preview'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_display.short_description = 'Created'
    
    def updated_at_display(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')
    updated_at_display.short_description = 'Updated'
    
    fieldsets = (
        ('Newsletter Content', {
            'fields': ('title', 'subtitle', 'image', 'image_preview_large'),
            'classes': ('wide',)
        }),
        ('Benefits List', {
            'fields': ('benefits', 'benefits_preview'),
            'description': 'Add each benefit on a new line. They will be displayed in two columns on the website.',
            'classes': ('wide',)
        }),
        ('PDF File', {
            'fields': ('pdf_file', 'pdf_link'),
            'description': 'Upload newsletter PDF for download. Max file size: 10MB',
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_active',),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse', 'wide')
        }),
    )
    
    def has_add_permission(self, request):
        return NewsletterContent.objects.count() == 0

# ============ FREE EBOOK ADMIN ============
@admin.register(FreeEbook)
class FreeEbookAdmin(admin.ModelAdmin):
    list_display = ['title', 'cover_preview', 'is_active', 'download_count', 'is_active_badge', 'created_at_display', 'updated_at_display', 'file_size_display']
    list_display_links = ['title']
    search_fields = ['title', 'subtitle', 'description']
    readonly_fields = ['created_at', 'updated_at', 'cover_preview_large', 'download_count', 'pdf_preview_large', 'download_stats', 'file_info']
    list_editable = ['is_active']
    actions = [make_active, make_inactive, 'reset_download_count', 'export_download_stats']
    list_per_page = 20
    
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 65px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />', 
                obj.cover_image.url
            )
        return format_html('<div style="width: 50px; height: 65px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 4px; color: #6c757d; font-size: 10px;">No Cover</div>')
    cover_preview.short_description = 'Cover'
    
    def cover_preview_large(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 260px; object-fit: contain; border-radius: 8px; border: 2px solid #ddd; margin: 10px 0;" />', 
                obj.cover_image.url
            )
        return format_html('<div style="width: 200px; height: 260px; background: #f8f9fa; border-radius: 8px; border: 2px dashed #ddd; display: flex; align-items: center; justify-content: center; color: #6c757d; margin: 10px 0;">No cover image</div>')
    cover_preview_large.short_description = 'Cover Preview'
    
    def file_size_display(self, obj):
        """Safe file size display that handles missing files"""
        try:
            if obj.ebook_file and obj.ebook_file.name:
                # Check if file exists before trying to get size
                try:
                    file_size = obj.ebook_file.size
                except (FileNotFoundError, OSError):
                    return "⚠️ File missing"
                
                # Format the size
                if file_size < 1024:
                    return f"{file_size} B"
                elif file_size < 1024 * 1024:
                    return f"{file_size / 1024:.1f} KB"
                elif file_size < 1024 * 1024 * 1024:
                    return f"{file_size / (1024 * 1024):.1f} MB"
                else:
                    return f"{file_size / (1024 * 1024 * 1024):.1f} GB"
            return "No file"
        except Exception as e:
            return "Error"
    file_size_display.short_description = 'File Size'
    
    def pdf_preview_large(self, obj):
        if obj.ebook_file:
            file_size = obj.ebook_file.size if obj.ebook_file else 0
            
            # Calculate size in appropriate units
            if file_size < 1024:
                size_display = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_display = f"{file_size / 1024:.1f} KB"
            elif file_size < 1024 * 1024 * 1024:
                size_display = f"{file_size / (1024 * 1024):.1f} MB"
            else:
                size_display = f"{file_size / (1024 * 1024 * 1024):.1f} GB"
            
            file_name = obj.ebook_file.name.split("/")[-1]
            file_extension = file_name.split('.')[-1].upper() if '.' in file_name else 'UNKNOWN'
            
            html = '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; margin: 10px 0;">'
            html += f'<h5 style="margin-top: 0; color: #053e91;">File Details:</h5>'
            html += f'<p style="margin: 5px 0;"><strong>File Name:</strong> {file_name}</p>'
            html += f'<p style="margin: 5px 0;"><strong>File Type:</strong> {file_extension}</p>'
            html += f'<p style="margin: 5px 0;"><strong>File Size:</strong> {size_display}</p>'
            html += f'<p style="margin: 5px 0;"><strong>Total Downloads:</strong> {obj.download_count}</p>'
            html += f'<a href="{obj.ebook_file.url}" target="_blank" style="background: #28a745; color: white; padding: 8px 15px; border-radius: 5px; text-decoration: none; display: inline-block; margin-top: 10px; margin-right: 10px;">'
            html += '<i class="fas fa-external-link-alt me-1"></i> Preview in New Tab</a>'
            html += f'<a href="{obj.ebook_file.url}" download style="background: #007bff; color: white; padding: 8px 15px; border-radius: 5px; text-decoration: none; display: inline-block; margin-top: 10px;">'
            html += '<i class="fas fa-download me-1"></i> Download File</a>'
            html += '</div>'
            return format_html(html)
        return format_html('<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; color: #6c757d; margin: 10px 0;">No eBook file uploaded</div>')
    pdf_preview_large.short_description = 'File Preview'
    
    def file_info(self, obj):
        if obj.ebook_file:
            html = '<div style="background: #e3f2fd; padding: 15px; border-radius: 8px; border: 1px solid #bbdefb; margin: 10px 0;">'
            html += '<h5 style="margin-top: 0; color: #1565c0;">File Information:</h5>'
            html += '<ul style="margin: 5px 0 0 0; padding-left: 20px;">'
            html += '<li><strong>Uploaded:</strong> ' + obj.created_at.strftime('%Y-%m-%d %H:%M') + '</li>'
            html += '<li><strong>Last Updated:</strong> ' + obj.updated_at.strftime('%Y-%m-%d %H:%M') + '</li>'
            html += '<li><strong>Current Status:</strong> ' + ('Active' if obj.is_active else 'Inactive') + '</li>'
            
            if obj.download_count > 0:
                html += f'<li><strong>Download Popularity:</strong> {obj.download_count} download{"s" if obj.download_count != 1 else ""}</li>'
                days_since_creation = (timezone.now() - obj.created_at).days or 1
                avg_daily = obj.download_count / days_since_creation
                html += f'<li><strong>Average Daily Downloads:</strong> {avg_daily:.1f}</li>'
            
            html += '</ul>'
            html += '<p style="margin: 10px 0 0 0; font-size: 0.9em; color: #0d47a1;"><i class="fas fa-info-circle me-1"></i> This eBook will be offered to newsletter subscribers as a free gift.</p>'
            html += '</div>'
            return format_html(html)
        return format_html('<div style="background: #fff3cd; padding: 15px; border-radius: 8px; border: 1px solid #ffecb5; color: #856404; margin: 10px 0;">'
                          '<i class="fas fa-exclamation-triangle me-1"></i> No eBook file uploaded. Please upload a file to make this eBook available to subscribers.'
                          '</div>')
    file_info.short_description = 'File Information'
    
    def download_stats(self, obj):
        html = '<div style="background: #e8f5e9; padding: 15px; border-radius: 8px; border: 1px solid #c3e6cb; margin: 10px 0;">'
        html += '<h5 style="margin-top: 0; color: #155724;">Download Statistics:</h5>'
        
        if obj.download_count > 0:
            html += f'<p style="margin: 5px 0;"><strong>Total Downloads:</strong> <span style="font-size: 1.2em; font-weight: bold; color: #28a745;">{obj.download_count}</span></p>'
            
            days_since_creation = (timezone.now() - obj.created_at).days or 1
            avg_daily = obj.download_count / days_since_creation
            
            html += f'<p style="margin: 5px 0;"><strong>Average daily:</strong> {avg_daily:.1f} downloads/day</p>'
            html += f'<p style="margin: 5px 0;"><strong>Created:</strong> {obj.created_at.strftime("%Y-%m-%d")} ({days_since_creation} days ago)</p>'
            
            if avg_daily > 5:
                performance = "Excellent"
                performance_color = "#28a745"
            elif avg_daily > 2:
                performance = "Good"
                performance_color = "#17a2b8"
            elif avg_daily > 0.5:
                performance = "Average"
                performance_color = "#ffc107"
            else:
                performance = "Low"
                performance_color = "#6c757d"
                
            html += f'<p style="margin: 5px 0;"><strong>Performance:</strong> <span style="color: {performance_color}; font-weight: bold;">{performance}</span></p>'
        else:
            html += '<p style="margin: 5px 0; color: #6c757d;"><i class="fas fa-info-circle me-1"></i> No downloads yet</p>'
            html += '<p style="margin: 5px 0; font-size: 0.9em;">Upload an eBook file and make it active to start tracking downloads.</p>'
        
        html += '</div>'
        return format_html(html)
    download_stats.short_description = 'Download Statistics'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Active</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_display.short_description = 'Created'
    
    def updated_at_display(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')
    updated_at_display.short_description = 'Updated'
    
    def reset_download_count(self, request, queryset):
        updated = queryset.update(download_count=0)
        messages.success(request, f"Reset download count to 0 for {updated} eBook(s)")
    reset_download_count.short_description = "🔄 Reset download count to 0"
    
    def export_download_stats(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ebook_download_stats.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Title', 'Downloads', 'File Size', 'Created', 'Last Updated', 'Status', 'File Name', 'Active'])
        
        for ebook in queryset:
            file_name = ebook.ebook_file.name.split('/')[-1] if ebook.ebook_file else 'No file'
            status = 'Active' if ebook.is_active else 'Inactive'
            file_size = ebook.ebook_file.size if ebook.ebook_file else 0
            
            # Format file size
            if file_size < 1024:
                size_display = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_display = f"{file_size / 1024:.1f} KB"
            elif file_size < 1024 * 1024 * 1024:
                size_display = f"{file_size / (1024 * 1024):.1f} MB"
            else:
                size_display = f"{file_size / (1024 * 1024 * 1024):.1f} GB"
            
            writer.writerow([
                ebook.title,
                ebook.download_count,
                size_display,
                ebook.created_at.strftime('%Y-%m-%d'),
                ebook.updated_at.strftime('%Y-%m-%d %H:%M'),
                status,
                file_name,
                'Yes' if ebook.is_active else 'No'
            ])
        
        return response
    export_download_stats.short_description = "📊 Export download statistics as CSV"
    
    fieldsets = (
        ('eBook Information', {
            'fields': ('title', 'subtitle', 'description'),
            'description': 'This eBook will be offered as a free gift to newsletter subscribers.',
            'classes': ('wide',)
        }),
        ('Cover Image (Optional)', {
            'fields': ('cover_image', 'cover_preview_large'),
            'description': 'Recommended size: 200x260 pixels. This will be displayed to users. Cover image is optional.',
            'classes': ('wide',)
        }),
        ('eBook File', {
            'fields': ('ebook_file', 'pdf_preview_large', 'file_info'),
            'description': 'Upload the eBook file that users will download. Accepts PDF, DOC, DOCX, EPUB, MOBI, and other document formats. <strong>No file size limit</strong> - upload files of any size.',
            'classes': ('wide',)
        }),
        ('Statistics', {
            'fields': ('download_count', 'download_stats'),
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_active',),
            'description': 'Only active eBooks will be shown on the website. Only one eBook can be active at a time.',
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse', 'wide')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if change and 'is_active' in form.changed_data and not obj.is_active:
            active_ebooks = FreeEbook.objects.filter(is_active=True).exclude(id=obj.id).count()
            if active_ebooks == 0:
                messages.warning(request, "No active eBooks will remain. Newsletter subscribers won't see any free eBook offer.")
        
        if change and 'is_active' in form.changed_data and obj.is_active:
            FreeEbook.objects.filter(is_active=True).exclude(id=obj.id).update(is_active=False)
            messages.info(request, "Other eBooks have been deactivated. Only one eBook can be active at a time.")
        
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        active_count = FreeEbook.objects.filter(is_active=True).count()
        if active_count > 0:
            messages.info(request, "There's already an active eBook. Adding a new one will require you to choose which one to activate.")
        return True
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-is_active', '-download_count', '-updated_at')
    
# ============ CONTACT SUBMISSION ADMIN ============
@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'organization', 'event_type', 'status', 'submitted_at']
    list_filter = ['status', 'event_type', 'submitted_at']
    list_editable = ['status']
    list_display_links = ['id']
    search_fields = ['full_name', 'email', 'organization', 'event_details']
    readonly_fields = ['submitted_at', 'contacted_at', 'event_details_display']
    date_hierarchy = 'submitted_at'
    actions = ['mark_as_contacted', 'mark_as_booked', 'mark_as_cancelled']
    list_per_page = 25
    
    def event_details_display(self, obj):
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; white-space: pre-wrap; max-height: 300px; overflow: auto;">{}</div>',
            obj.event_details
        )
    event_details_display.short_description = 'Event Details'
    
    def mark_as_contacted(self, request, queryset):
        updated = queryset.update(status='contacted', contacted_at=timezone.now())
        messages.success(request, f"{updated} submissions marked as contacted")
    mark_as_contacted.short_description = "📞 Mark selected as contacted"
    
    def mark_as_booked(self, request, queryset):
        updated = queryset.update(status='booked')
        messages.success(request, f"{updated} submissions marked as booked")
    mark_as_booked.short_description = "✅ Mark selected as booked"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        messages.success(request, f"{updated} submissions marked as cancelled")
    mark_as_cancelled.short_description = "❌ Mark selected as cancelled"
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('full_name', 'email', 'organization'),
            'classes': ('wide',)
        }),
        ('Event Details', {
            'fields': ('event_type', 'event_details_display'),
            'classes': ('wide',)
        }),
        ('Status & Follow-up', {
            'fields': ('status', 'contacted_at', 'notes'),
            'classes': ('wide',)
        }),
        ('Submission Time', {
            'fields': ('submitted_at',),
            'classes': ('collapse', 'wide')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data and obj.status == 'contacted':
            obj.contacted_at = timezone.now()
        super().save_model(request, obj, form, change)

# ============ NEWSLETTER SUBSCRIPTION ADMIN ============
@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'source_display', 'status_display', 'subscribed_at_display']
    list_filter = ['source', 'is_active']
    list_display_links = ['email']
    search_fields = ['email', 'name']
    actions = [make_active, make_inactive, 'export_emails']
    list_per_page = 50
    
    def source_display(self, obj):
        colors = {
            'newsletter_section': '#28a745',
            'footer': '#17a2b8'
        }
        color = colors.get(obj.source, '#6c757d')
        display_text = dict(obj.SOURCE_CHOICES).get(obj.source, obj.source)
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color,
            display_text
        )
    source_display.short_description = 'Source'
    
    def status_display(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Active</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">Inactive</span>'
        )
    status_display.short_description = 'Status'
    
    def subscribed_at_display(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')
        return 'N/A'
    subscribed_at_display.short_description = 'Subscribed'
    
    def export_emails(self, request, queryset):
        emails = list(queryset.values_list('email', flat=True))
        email_list = '\n'.join(emails)
        response = HttpResponse(email_list, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="newsletter_emails.txt"'
        return response
    export_emails.short_description = "📧 Export selected emails"
    
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('name', 'email', 'source'),
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_active', 'agreed_to_terms'),
            'classes': ('wide',)
        }),
    )

# ============ SYSTEM LOG ADMIN ============
@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['log_level_badge', 'message_truncated', 'source', 'created_at_display']
    list_filter = ['log_level', 'source', 'created_at']
    search_fields = ['message', 'source']
    readonly_fields = ['created_at', 'user_ip', 'user_agent', 'full_message']
    date_hierarchy = 'created_at'
    actions = ['clear_old_logs']
    list_per_page = 50
    
    def log_level_badge(self, obj):
        color_map = {
            'info': '#17a2b8',
            'warning': '#ffc107',
            'error': '#dc3545',
            'success': '#28a745'
        }
        color = color_map.get(obj.log_level, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            color,
            obj.get_log_level_display().upper()
        )
    log_level_badge.short_description = 'Level'
    
    def message_truncated(self, obj):
        if len(obj.message) > 80:
            return f"{obj.message[:80]}..."
        return obj.message
    message_truncated.short_description = 'Message'
    
    def full_message(self, obj):
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; white-space: pre-wrap; font-family: monospace;">{}</div>',
            obj.message
        )
    full_message.short_description = 'Full Message'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    created_at_display.short_description = 'Created'
    
    def clear_old_logs(self, request, queryset):
        cutoff_date = timezone.now() - timedelta(days=30)
        old_logs = SystemLog.objects.filter(created_at__lt=cutoff_date)
        count = old_logs.count()
        old_logs.delete()
        messages.success(request, f"Cleared {count} logs older than 30 days")
    clear_old_logs.short_description = "🗑️ Clear logs older than 30 days"
    
    fieldsets = (
        ('Log Details', {
            'fields': ('log_level', 'message', 'full_message', 'source'),
            'classes': ('wide',)
        }),
        ('User Information', {
            'fields': ('user_ip', 'user_agent'),
            'classes': ('collapse', 'wide')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse', 'wide')
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

# ============ FORM SUBMISSION ADMIN ============
@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'submitted_data_preview', 'submitted_at']
    list_filter = ['submitted_at']
    list_display_links = ['id']
    search_fields = ['form_data']
    readonly_fields = ['submitted_at', 'form_data_display']
    date_hierarchy = 'submitted_at'
    actions = [export_as_json]
    list_per_page = 30
    
    def submitted_data_preview(self, obj):
        """Display form data preview"""
        try:
            data = json.loads(obj.form_data)
            preview = json.dumps(data, ensure_ascii=False)[:80]
            if len(json.dumps(data, ensure_ascii=False)) > 80:
                preview += '...'
            return preview
        except:
            return obj.form_data[:80] + '...' if len(obj.form_data) > 80 else obj.form_data
    submitted_data_preview.short_description = 'Form Data'
    
    def form_data_display(self, obj):
        """Display formatted form data"""
        try:
            data = json.loads(obj.form_data)
            formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
            return format_html(
                '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; font-family: monospace; white-space: pre-wrap; max-height: 400px; overflow: auto;">{}</div>',
                formatted_json
            )
        except:
            return format_html(
                '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; font-family: monospace; white-space: pre-wrap; max-height: 400px; overflow: auto;">{}</div>',
                obj.form_data
            )
    form_data_display.short_description = 'Form Data (Formatted)'
    
    fieldsets = (
        ('Submission Details', {
            'fields': ('form_data_display',),
            'classes': ('wide',)
        }),
        ('Timestamp', {
            'fields': ('submitted_at',),
            'classes': ('collapse', 'wide')
        }),
    )
    
    def has_add_permission(self, request):
        """Disable add permission"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable change permission"""
        return False

# Add custom admin action for eBook analytics
def track_ebook_performance(modeladmin, request, queryset):
    for ebook in queryset:
        days_since_creation = (timezone.now() - ebook.created_at).days or 1
        avg_daily = ebook.download_count / days_since_creation
        
        messages.info(request, 
            f"'{ebook.title}': {ebook.download_count} downloads total, "
            f"{avg_daily:.1f} avg/day over {days_since_creation} days"
        )
track_ebook_performance.short_description = "📈 Show eBook performance analytics"
FreeEbookAdmin.actions.append(track_ebook_performance)

