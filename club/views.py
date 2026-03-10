import json
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as django_settings

from .models import (
    Member, Event, EventRegistration, Workshop, Achievement,
    GalleryImage, Certificate, Testimonial, ContactMessage,
    NewsletterSubscriber, ChatbotLog
)
from .forms import (
    MembershipForm, ContactForm, EventForm, AchievementForm,
    GalleryForm, CertificateForm
)


# ═══════════════════════════════════════════
#  PUBLIC PAGES
# ═══════════════════════════════════════════

def index(request):
    events = Event.objects.filter(is_active=True)[:3]
    workshops = Workshop.objects.filter(is_active=True)[:4]
    achievements = Achievement.objects.all()[:4]
    gallery = GalleryImage.objects.all()[:6]
    testimonials = Testimonial.objects.filter(is_active=True)[:3]
    members_count = Member.objects.filter(status='approved').count()
    events_count = Event.objects.count()
    workshops_count = Workshop.objects.count()
    return render(request, 'index.html', {
        'events': events, 'workshops': workshops, 'achievements': achievements,
        'gallery': gallery, 'testimonials': testimonials,
        'members_count': members_count, 'events_count': events_count,
        'workshops_count': workshops_count,
    })


def about(request):
    return render(request, 'about.html')


def events_page(request):
    events = Event.objects.filter(is_active=True)
    return render(request, 'events.html', {'events': events})


def workshops_page(request):
    workshops = Workshop.objects.filter(is_active=True)
    return render(request, 'workshops.html', {'workshops': workshops})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


def membership(request):
    if request.method == 'POST':
        form = MembershipForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save()
            messages.success(request,
                f'Registration successful! Your Registration ID is: {member.registration_id}. '
                f'You have been assigned to: {member.team_assigned}')
            return redirect('membership')
    else:
        form = MembershipForm()
    return render(request, 'membership.html', {'form': form})


# ═══════════════════════════════════════════
#  API ENDPOINTS (AJAX)
# ═══════════════════════════════════════════

@csrf_exempt
def api_newsletter(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'})
    email = request.POST.get('email', '').strip()
    if not email:
        return JsonResponse({'success': False, 'message': 'Email is required.'})
    sub, created = NewsletterSubscriber.objects.get_or_create(email=email, defaults={'is_active': True})
    if not created:
        if sub.is_active:
            return JsonResponse({'success': False, 'message': 'Already subscribed!'})
        sub.is_active = True
        sub.save()
    return JsonResponse({'success': True, 'message': 'Successfully subscribed! 🎉'})


@csrf_exempt
def api_event_register(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'})
    event_id = request.POST.get('event_id')
    name = request.POST.get('member_name', '').strip()
    email = request.POST.get('member_email', '').strip()
    phone = request.POST.get('member_phone', '').strip()
    reg_id = request.POST.get('registration_id', '').strip()

    if not event_id or not name or not email:
        return JsonResponse({'success': False, 'message': 'Name and email are required.'})

    event = Event.objects.filter(id=event_id, is_active=True).first()
    if not event:
        return JsonResponse({'success': False, 'message': 'Event not found.'})
    if event.is_full:
        return JsonResponse({'success': False, 'message': 'Event is full.'})
    if EventRegistration.objects.filter(event=event, email=email).exists():
        return JsonResponse({'success': False, 'message': 'Already registered for this event.'})

    member = None
    if reg_id:
        member = Member.objects.filter(registration_id=reg_id).first()

    EventRegistration.objects.create(event=event, member=member, participant_name=name, email=email, phone=phone)
    return JsonResponse({'success': True, 'message': 'Registration successful!', 'data': {'event': event.title}})


@csrf_exempt
def api_chatbot(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'})

    # Accept both form-encoded and JSON
    content_type = request.content_type or ''
    if 'json' in content_type:
        try:
            body = json.loads(request.body)
            user_msg = body.get('message', '').strip()
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON'})
    else:
        user_msg = request.POST.get('message', '').strip()

    if not user_msg:
        return JsonResponse({'success': False, 'message': 'Message required'})

    reply = get_chatbot_response(user_msg)

    ChatbotLog.objects.create(
        session_id=request.session.session_key or 'anonymous',
        user_message=user_msg,
        bot_response=reply
    )
    return JsonResponse({'success': True, 'response': reply})


def get_chatbot_response(message):
    msg = message.lower().strip()
    responses = {
        r'join|register|member|signup|sign up':
            "We'd love to have you! 🎉 Head to our <a href='/membership/'>Membership page</a> to register. It's free — you'll get a unique Registration ID and be auto-assigned to a team!",
        r'event|quiz|debate|poster|competition|contest|caricature':
            "We host Quiz Competitions, Debates, Poster-Making Contests, and more! 🏆 Check our <a href='/events/'>Events page</a>.",
        r'workshop|learn|course|training|skill':
            "Our workshops cover Web Dev, AI/ML, UI/UX Design, Cybersecurity and more! 💻 Visit <a href='/workshops/'>Workshops</a>.",
        r'team|assign|allocation':
            "We have 4 teams: Technical, Media, Event, and Industry Collaboration. Our AI assigns you based on your skills! 🤖",
        r'certificate|cert':
            "Yes! We provide certificates for event participation. You can download them after the event. 📜",
        r'achievement|award|win':
            "Our members have many achievements! Check the <a href='/#achievements'>Achievements section</a>. 🌟",
        r'contact|reach|email|help':
            "Reach us at info@womenovatorsclub.com or visit <a href='/contact/'>Contact page</a>. 📧",
        r'about|who|what is|womenovator':
            "Womenovators Club empowers women in tech. Mission: Empower, Educate, Elevate! 💜 <a href='/about/'>Learn more</a>.",
        r'hello|hi|hey|good morning|good evening':
            "Hello! 👋 Welcome to Womenovators Club! Ask about membership, events, workshops, or anything!",
        r'thank|thanks':
            "You're welcome! 😊 Ask anytime!",
        r'bye|goodbye':
            "Bye! 👋 Check out our upcoming events. See you soon!",
        r'fee|cost|price|pay|money':
            "Great news — membership is completely FREE! 🎉",
        r'benefit|advantage|why join':
            "Members enjoy: free workshops, certificates, networking, team projects, leadership roles, and more! 🌟",
        r'gallery|photo|image':
            "Check our <a href='/#gallery'>Gallery</a> on the homepage! 📷",
    }

    for pattern, reply in responses.items():
        if re.search(pattern, msg):
            return reply

    return ("That's a great question! 🤔 You can:\n• <a href='/about/'>Learn about us</a>\n"
            "• <a href='/events/'>See events</a>\n• <a href='/workshops/'>Explore workshops</a>\n"
            "• <a href='/contact/'>Contact us</a>\n\nOr ask about membership, events, or workshops!")


# ═══════════════════════════════════════════
#  ADMIN DASHBOARD
# ═══════════════════════════════════════════

def dashboard_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'dashboard/login.html')


def dashboard_logout(request):
    logout(request)
    return redirect('dashboard_login')


@login_required
def dashboard(request):
    ctx = {
        'total_members': Member.objects.count(),
        'pending_members': Member.objects.filter(status='pending').count(),
        'total_events': Event.objects.count(),
        'total_registrations': EventRegistration.objects.count(),
        'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
        'total_subscribers': NewsletterSubscriber.objects.filter(is_active=True).count(),
        'recent_members': Member.objects.all()[:5],
        'recent_messages': ContactMessage.objects.all()[:5],
    }
    # Monthly chart data
    from django.db.models.functions import ExtractMonth
    monthly = (Member.objects
               .filter(created_at__year=2026)
               .annotate(month=ExtractMonth('created_at'))
               .values('month')
               .annotate(count=Count('id'))
               .order_by('month'))
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    chart_data = [0] * 12
    for row in monthly:
        chart_data[row['month'] - 1] = row['count']
    ctx['chart_labels'] = json.dumps(month_names)
    ctx['chart_data'] = json.dumps(chart_data)

    # Team distribution
    teams = Member.objects.exclude(team_assigned='').values('team_assigned').annotate(count=Count('id'))
    ctx['team_labels'] = json.dumps([t['team_assigned'] for t in teams] or ['No data'])
    ctx['team_counts'] = json.dumps([t['count'] for t in teams] or [1])

    return render(request, 'dashboard/dashboard.html', ctx)


@login_required
def manage_members(request):
    # Handle actions via GET params
    action = request.GET.get('action')
    member_id = request.GET.get('id')
    if action and member_id:
        member = get_object_or_404(Member, id=member_id)
        if action == 'approve':
            member.status = 'approved'
            member.save()
            messages.success(request, f'{member.full_name} approved!')
        elif action == 'reject':
            member.status = 'rejected'
            member.save()
            messages.warning(request, f'{member.full_name} rejected.')
        elif action == 'delete':
            member.delete()
            messages.error(request, 'Member deleted.')
        return redirect('manage_members')

    qs = Member.objects.all()
    status = request.GET.get('status')
    team = request.GET.get('team')
    search = request.GET.get('search', '')
    if status:
        qs = qs.filter(status=status)
    if team:
        qs = qs.filter(team_assigned=team)
    if search:
        qs = qs.filter(Q(full_name__icontains=search) | Q(email__icontains=search) | Q(registration_id__icontains=search))

    return render(request, 'dashboard/members.html', {
        'members': qs, 'search': search, 'status_filter': status or '', 'team_filter': team or ''
    })


@login_required
def manage_events(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            form = EventForm(request.POST, request.FILES)
            if form.is_valid():
                event = form.save(commit=False)
                event.slug = slugify(event.title)
                # Ensure unique slug
                base_slug = event.slug
                counter = 1
                while Event.objects.filter(slug=event.slug).exists():
                    event.slug = f'{base_slug}-{counter}'
                    counter += 1
                event.save()
                messages.success(request, f"Event '{event.title}' created!")
        elif action == 'update':
            event = get_object_or_404(Event, id=request.POST.get('event_id'))
            form = EventForm(request.POST, request.FILES, instance=event)
            if form.is_valid():
                form.save()
                messages.success(request, 'Event updated!')
        elif action == 'delete':
            Event.objects.filter(id=request.POST.get('event_id')).delete()
            messages.error(request, 'Event deleted.')
        elif action == 'toggle_status':
            event = get_object_or_404(Event, id=request.POST.get('event_id'))
            event.is_active = not event.is_active
            event.save()
            messages.info(request, 'Status toggled.')
        return redirect('manage_events')

    events = Event.objects.annotate(reg_count=Count('eventregistration'))
    return render(request, 'dashboard/events.html', {'events': events, 'form': EventForm()})


@login_required
def manage_achievements(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            form = AchievementForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Achievement added!')
        elif action == 'delete':
            Achievement.objects.filter(id=request.POST.get('achievement_id')).delete()
            messages.error(request, 'Achievement deleted.')
        return redirect('manage_achievements')

    return render(request, 'dashboard/achievements.html', {
        'achievements': Achievement.objects.all(), 'form': AchievementForm()
    })


@login_required
def manage_gallery(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'upload':
            form = GalleryForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Image uploaded!')
        elif action == 'delete':
            GalleryImage.objects.filter(id=request.POST.get('gallery_id')).delete()
            messages.error(request, 'Image removed.')
        return redirect('manage_gallery')

    category = request.GET.get('category', '')
    qs = GalleryImage.objects.all()
    if category:
        qs = qs.filter(category=category)
    return render(request, 'dashboard/gallery.html', {
        'gallery': qs, 'category_filter': category, 'form': GalleryForm(), 'events': Event.objects.all()
    })


@login_required
def manage_certificates(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'generate':
            member_id = request.POST.get('member')
            event_id = request.POST.get('event')
            issued_by = request.POST.get('issued_by', request.user.get_full_name() or request.user.username)
            if member_id and event_id:
                if Certificate.objects.filter(member_id=member_id, event_id=event_id).exists():
                    messages.warning(request, 'Certificate already exists for this combo.')
                else:
                    cert = Certificate(member_id=member_id, event_id=event_id, issued_by=issued_by)
                    cert.save()
                    messages.success(request, f'Certificate {cert.certificate_number} generated!')
        elif action == 'bulk_generate':
            event_id = request.POST.get('event')
            issued_by = request.POST.get('issued_by', request.user.get_full_name() or request.user.username)
            if event_id:
                regs = EventRegistration.objects.filter(event_id=event_id, member__isnull=False)
                count = 0
                for reg in regs:
                    if not Certificate.objects.filter(member=reg.member, event_id=event_id).exists():
                        cert = Certificate(member=reg.member, event_id=event_id, issued_by=issued_by)
                        cert.save()
                        count += 1
                messages.success(request, f'{count} certificates generated.')
        elif action == 'delete':
            Certificate.objects.filter(id=request.POST.get('cert_id')).delete()
            messages.error(request, 'Certificate deleted.')
        return redirect('manage_certificates')

    return render(request, 'dashboard/certificates.html', {
        'certificates': Certificate.objects.select_related('member', 'event').all(),
        'members': Member.objects.filter(status='approved'),
        'events': Event.objects.all(),
        'admin_name': request.user.get_full_name() or request.user.username,
    })


def certificate_view(request, cert_id):
    cert = get_object_or_404(Certificate.objects.select_related('member', 'event'), id=cert_id)
    return render(request, 'certificate_view.html', {'cert': cert})
