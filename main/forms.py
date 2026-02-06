from django import forms
from .models import ContactSubmission, NewsletterSubscription

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ['full_name', 'email', 'organization', 'event_type', 'event_details']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Work Email',
                'required': True
            }),
            'organization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Organization Name',
                'required': True
            }),
            'event_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'event_details': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us about your event...',
                'rows': 4,
                'required': True
            }),
        }

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['name', 'email', 'source']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email',
                'required': True
            }),
            'source': forms.HiddenInput(),
        }