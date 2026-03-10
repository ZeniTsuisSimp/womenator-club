import datetime
import re
from django.db import models
from django.utils import timezone


class Member(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]
    TEAM_CHOICES = [
        ('Technical Team', 'Technical Team'),
        ('Media Team', 'Media Team'),
        ('Event Team', 'Event Team'),
        ('Industry Collaboration Team', 'Industry Collaboration Team'),
    ]

    registration_id = models.CharField(max_length=20, unique=True, editable=False)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    department = models.CharField(max_length=100)
    year_semester = models.CharField(max_length=50)
    skills = models.TextField(blank=True, default='')
    achievements = models.TextField(blank=True, default='')
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    college_id_file = models.FileField(upload_to='ids/', blank=True, null=True)
    achievement_proof = models.FileField(upload_to='achievements/', blank=True, null=True)
    team_assigned = models.CharField(max_length=50, choices=TEAM_CHOICES, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.registration_id} - {self.full_name}"

    def save(self, *args, **kwargs):
        if not self.registration_id:
            self.registration_id = self.generate_registration_id()
        if not self.team_assigned and self.skills:
            self.team_assigned = self.assign_team()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_registration_id():
        year = timezone.now().year
        last = Member.objects.filter(registration_id__startswith=f'WN-{year}').order_by('-registration_id').first()
        if last:
            num = int(last.registration_id.split('-')[-1]) + 1
        else:
            num = 1
        return f'WN-{year}-{num:03d}'

    def assign_team(self):
        skills_lower = self.skills.lower()
        coding = ['python', 'java', 'c++', 'coding', 'programming', 'web', 'html', 'css', 'javascript',
                   'react', 'django', 'flask', 'database', 'sql', 'backend', 'frontend', 'fullstack',
                   'api', 'software', 'machine learning', 'ai', 'data science', 'cyber']
        design = ['design', 'photoshop', 'illustrator', 'figma', 'canva', 'ui', 'ux', 'graphic',
                  'video', 'editing', 'photography', 'media', 'content', 'animation', 'social media']
        leadership = ['leadership', 'management', 'event', 'organize', 'coordinate', 'planning',
                      'communication', 'public speaking', 'team lead', 'volunteer']
        networking = ['networking', 'business', 'marketing', 'industry', 'entrepreneurship',
                      'collaboration', 'outreach', 'partnership', 'liaison', 'sponsor']

        scores = {
            'Technical Team': sum(1 for k in coding if k in skills_lower),
            'Media Team': sum(1 for k in design if k in skills_lower),
            'Event Team': sum(1 for k in leadership if k in skills_lower),
            'Industry Collaboration Team': sum(1 for k in networking if k in skills_lower),
        }
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else 'Technical Team'


class Event(models.Model):
    TYPE_CHOICES = [('Quiz', 'Quiz'), ('Debate', 'Debate'), ('Poster Making', 'Poster Making'),
                    ('Caricature', 'Caricature'), ('Workshop', 'Workshop')]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    event_date = models.DateField()
    event_time = models.TimeField(blank=True, null=True)
    venue = models.CharField(max_length=200, blank=True)
    max_participants = models.PositiveIntegerField(default=100)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-event_date']

    def __str__(self):
        return self.title

    @property
    def registration_count(self):
        return self.eventregistration_set.count()

    @property
    def is_full(self):
        return self.registration_count >= self.max_participants


class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)
    participant_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'email')
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.participant_name} - {self.event.title}"


class Workshop(models.Model):
    LEVEL_CHOICES = [('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')]

    title = models.CharField(max_length=200)
    instructor = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration = models.CharField(max_length=50, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Beginner')
    image = models.ImageField(upload_to='workshops/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Achievement(models.Model):
    CATEGORY_CHOICES = [('Competition', 'Competition'), ('Academic', 'Academic'),
                        ('Project', 'Project'), ('Community', 'Community'), ('Leadership', 'Leadership')]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    member_name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Competition')
    achievement_date = models.DateField()
    image = models.ImageField(upload_to='achievements/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-achievement_date']

    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    CATEGORY_CHOICES = [('Events', 'Events'), ('Workshops', 'Workshops'),
                        ('Team', 'Team'), ('Activities', 'Activities')]

    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='gallery/')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Events')
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or f"Gallery #{self.id}"


class Certificate(models.Model):
    certificate_number = models.CharField(max_length=30, unique=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    issued_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('member', 'event')
        ordering = ['-created_at']

    def __str__(self):
        return self.certificate_number

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            self.certificate_number = self.generate_number()
        super().save(*args, **kwargs)

    def generate_number(self):
        year = timezone.now().year
        prefix = f'CERT-{year}-{int(self.event_id):03d}'
        last = Certificate.objects.filter(certificate_number__startswith=prefix).order_by('-certificate_number').first()
        if last:
            num = int(last.certificate_number.split('-')[-1]) + 1
        else:
            num = 1
        return f'{prefix}-{num:04d}'


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='photos/', blank=True, null=True)
    rating = models.PositiveSmallIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.rating}★"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}: {self.subject}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class ChatbotLog(models.Model):
    session_id = models.CharField(max_length=100)
    user_message = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
