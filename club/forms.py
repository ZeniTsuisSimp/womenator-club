from django import forms
from .models import Member, ContactMessage, EventRegistration, Event, Achievement, GalleryImage, Certificate


TECHNICAL_INTEREST_CHOICES = [
    ('Web Development', 'Web Development'),
    ('Artificial Intelligence', 'Artificial Intelligence'),
    ('Data Science', 'Data Science'),
    ('Python Programming', 'Python Programming'),
    ('UI/UX Design', 'UI/UX Design'),
    ('Cyber Security', 'Cyber Security'),
]


class MembershipForm(forms.ModelForm):
    technical_interests = forms.MultipleChoiceField(
        choices=TECHNICAL_INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    declaration = forms.BooleanField(
        required=True,
        label='I declare that the information provided is correct and I agree to actively participate in the activities of Womenator Club.',
    )

    class Meta:
        model = Member
        fields = ['full_name', 'email', 'phone', 'department', 'year_semester',
                  'college_name', 'membership_category', 'skills', 'technical_interests',
                  'achievements', 'photo', 'college_id_file', 'achievement_proof']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number', 'pattern': '[0-9]{10}'}),
            'college_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'College Name'}),
            'membership_category': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Select Department'),
                ('Computer Science', 'Computer Science'),
                ('Information Technology', 'Information Technology'),
                ('Electronics', 'Electronics'),
                ('Electrical', 'Electrical'),
                ('Mechanical', 'Mechanical'),
                ('Civil', 'Civil'),
                ('Data Science', 'Data Science'),
                ('AI & ML', 'AI & ML'),
                ('Other', 'Other'),
            ]),
            'year_semester': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Select Year/Semester'),
                ('1st Year - Sem 1', '1st Year - Sem 1'), ('1st Year - Sem 2', '1st Year - Sem 2'),
                ('2nd Year - Sem 3', '2nd Year - Sem 3'), ('2nd Year - Sem 4', '2nd Year - Sem 4'),
                ('3rd Year - Sem 5', '3rd Year - Sem 5'), ('3rd Year - Sem 6', '3rd Year - Sem 6'),
                ('4th Year - Sem 7', '4th Year - Sem 7'), ('4th Year - Sem 8', '4th Year - Sem 8'),
            ]),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Your Skills (comma separated)\nE.g.: Programming, Graphic Design, Public Speaking, Event Management'}),
            'achievements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Academic awards, competitions, certifications, leadership experience'}),
        }

    def clean_technical_interests(self):
        return ', '.join(self.cleaned_data.get('technical_interests', []))


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Your Message'}),
        }


class EventRegistrationForm(forms.Form):
    event_id = forms.IntegerField(widget=forms.HiddenInput())
    member_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    member_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    member_phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    registration_id = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))


# ── Admin dashboard forms ──

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'type', 'description', 'event_date', 'event_time', 'venue', 'max_participants', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'event_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'event_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'venue': forms.TextInput(attrs={'class': 'form-control'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['title', 'description', 'member_name', 'category', 'achievement_date', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'member_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'achievement_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class GalleryForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['title', 'image', 'category', 'event']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'event': forms.Select(attrs={'class': 'form-select'}),
        }


class CertificateForm(forms.Form):
    member = forms.ModelChoiceField(queryset=Member.objects.filter(status='approved'), widget=forms.Select(attrs={'class': 'form-select'}))
    event = forms.ModelChoiceField(queryset=Event.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    issued_by = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
