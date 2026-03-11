from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('events/', views.events_page, name='events'),
    path('workshops/', views.workshops_page, name='workshops'),
    path('contact/', views.contact, name='contact'),
    path('membership/', views.membership, name='membership'),

    # API endpoints
    path('api/newsletter/', views.api_newsletter, name='api_newsletter'),
    path('api/event-register/', views.api_event_register, name='api_event_register'),
    path('api/chatbot/', views.api_chatbot, name='api_chatbot'),

    # Certificate view
    path('certificate/<int:cert_id>/', views.certificate_view, name='certificate_view'),

    # Admin dashboard
    path('dashboard/login/', views.dashboard_login, name='dashboard_login'),
    path('dashboard/logout/', views.dashboard_logout, name='dashboard_logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/members/', views.manage_members, name='manage_members'),
    path('dashboard/members/<int:member_id>/', views.member_profile, name='member_profile'),
    path('dashboard/events/', views.manage_events, name='manage_events'),
    path('dashboard/events/<int:event_id>/participants/', views.event_participants, name='event_participants'),
    path('dashboard/achievements/', views.manage_achievements, name='manage_achievements'),
    path('dashboard/gallery/', views.manage_gallery, name='manage_gallery'),
    path('dashboard/certificates/', views.manage_certificates, name='manage_certificates'),
]
