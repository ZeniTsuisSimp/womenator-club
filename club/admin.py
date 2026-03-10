from django.contrib import admin
from .models import (
    Member, Event, EventRegistration, Workshop, Achievement,
    GalleryImage, Certificate, Testimonial, ContactMessage,
    NewsletterSubscriber, ChatbotLog
)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['registration_id', 'full_name', 'email', 'team_assigned', 'status', 'created_at']
    list_filter = ['status', 'team_assigned']
    search_fields = ['full_name', 'email', 'registration_id']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'event_date', 'venue', 'is_active']
    list_filter = ['type', 'is_active']
    search_fields = ['title']


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['event', 'participant_name', 'email', 'registered_at']
    list_filter = ['event']


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'level', 'duration']
    list_filter = ['level']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'member_name', 'achievement_date']
    list_filter = ['category']


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_at']
    list_filter = ['category']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_number', 'member', 'event', 'created_at']
    search_fields = ['certificate_number']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'rating', 'is_active']
    list_filter = ['is_active']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read']


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_at', 'is_active']


@admin.register(ChatbotLog)
class ChatbotLogAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user_message', 'created_at']
    search_fields = ['session_id']
