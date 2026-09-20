from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import DietPlan, Member, Payment, Progress, Trainer, User, WorkoutPlan


class BootstrapFormMixin:
    def _apply_bootstrap(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.RadioSelect, forms.CheckboxSelectMultiple)):
                continue
            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css = 'form-select'
            elif isinstance(widget, forms.CheckboxInput):
                css = 'form-check-input'
            else:
                css = 'form-control'
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = f'{existing} {css}'.strip()
            if isinstance(field, forms.DecimalField):
                widget.attrs.setdefault('step', '0.01')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class LoginForm(BootstrapFormMixin, forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    role = forms.ChoiceField(
        label='Role',
        choices=User.Role.choices,
        widget=forms.RadioSelect,
        initial=User.Role.MEMBER,
    )


class MemberDetailsMixin(forms.Form):
    GOAL_CHOICES = [
        ('Weight Loss', 'Weight Loss'),
        ('Muscle Gain', 'Muscle Gain'),
        ('Body Building', 'Body Building'),
        ('Fitness Maintenance', 'Fitness Maintenance'),
        ('General Fitness', 'General Fitness'),
    ]

    fullname = forms.CharField(label='Full Name', max_length=150)
    dob = forms.DateField(label='Date of Birth', widget=forms.DateInput(attrs={'type': 'date'}))
    age = forms.IntegerField(label='Age', min_value=1, max_value=120)
    gender = forms.ChoiceField(label='Gender', choices=Member.GENDER_CHOICES)
    phone = forms.CharField(label='Phone Number', max_length=20)
    email = forms.EmailField(label='Email Address')
    height = forms.DecimalField(
        label='Height (cm)',
        min_value=50,
        max_value=250,
        decimal_places=2,
        max_digits=5,
    )
    weight = forms.DecimalField(
        label='Weight (kg)',
        min_value=20,
        max_value=400,
        decimal_places=2,
        max_digits=5,
    )
    address = forms.CharField(label='Address', widget=forms.Textarea(attrs={'rows': 3}))
    goal = forms.ChoiceField(label='Fitness Goal', choices=GOAL_CHOICES)

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        qs = Member.objects.filter(phone=phone)
        if getattr(self, 'instance_member', None):
            qs = qs.exclude(pk=self.instance_member.pk)
        if qs.exists():
            raise ValidationError('This phone number is already registered.')
        return phone

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data['email'])
        qs = User.objects.filter(email__iexact=email)
        if getattr(self, 'instance_user', None):
            qs = qs.exclude(pk=self.instance_user.pk)
        if qs.exists():
            raise ValidationError('This email address is already registered.')
        return email


class MemberRegistrationForm(BootstrapFormMixin, MemberDetailsMixin):
    password = forms.CharField(label='Password', widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        confirm = cleaned.get('confirm_password')
        if password and confirm and password != confirm:
            self.add_error('confirm_password', 'Password confirmation must match.')
        return cleaned


class TrainerForm(BootstrapFormMixin, forms.Form):
    fullname = forms.CharField(label='Trainer Name', max_length=150)
    phone = forms.CharField(label='Phone', max_length=20)
    email = forms.EmailField(label='Email')
    specialization = forms.CharField(label='Specialization', max_length=150)
    qualification = forms.CharField(label='Qualification', max_length=150)
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        required=False,
        help_text='Leave blank to keep the current password when editing.',
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        self.require_password = kwargs.pop('require_password', True)
        super().__init__(*args, **kwargs)
        if self.require_password:
            self.fields['password'].required = True
            self.fields['password'].help_text = ''
        if self.instance:
            self.fields['fullname'].initial = self.instance.fullname
            self.fields['phone'].initial = self.instance.phone
            self.fields['email'].initial = self.instance.email
            self.fields['specialization'].initial = self.instance.specialization
            self.fields['qualification'].initial = self.instance.qualification

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data['email'])
        qs = User.objects.filter(email__iexact=email)
        if self.instance:
            qs = qs.exclude(pk=self.instance.user_id)
        if qs.exists():
            raise ValidationError('This email address is already registered.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password)
        elif self.require_password:
            raise ValidationError('Password is required.')
        return password


class AssignTrainerForm(BootstrapFormMixin, forms.Form):
    member = forms.ModelChoiceField(queryset=Member.objects.none(), label='Member')
    trainer = forms.ModelChoiceField(queryset=Trainer.objects.none(), label='Trainer')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['member'].queryset = Member.objects.select_related('user', 'trainer').order_by('fullname')
        self.fields['trainer'].queryset = Trainer.objects.order_by('fullname')


class AssignedMemberFormMixin:
    def __init__(self, *args, **kwargs):
        trainer = kwargs.pop('trainer')
        super().__init__(*args, **kwargs)
        self.fields['member'].queryset = trainer.assigned_members.order_by('fullname')
        self.fields['member'].label = 'Member Name'


class WorkoutPlanForm(BootstrapFormMixin, AssignedMemberFormMixin, forms.ModelForm):
    class Meta:
        model = WorkoutPlan
        fields = ['member', 'workout_name', 'exercise_type', 'duration', 'sets', 'repetitions', 'instructions']
        labels = {
            'workout_name': 'Workout Name',
            'exercise_type': 'Workout Type',
            'duration': 'Duration',
            'sets': 'Sets',
            'repetitions': 'Repetitions',
            'instructions': 'Trainer Notes',
        }


class DietPlanForm(BootstrapFormMixin, AssignedMemberFormMixin, forms.ModelForm):
    class Meta:
        model = DietPlan
        fields = ['member', 'breakfast', 'lunch', 'dinner', 'snacks', 'instructions']
        labels = {
            'instructions': 'Additional Instructions',
        }


class ProgressForm(BootstrapFormMixin, AssignedMemberFormMixin, forms.ModelForm):
    bmi = forms.CharField(
        label='BMI',
        required=False,
        disabled=True,
        help_text='Calculated automatically from member height and weight.',
    )

    class Meta:
        model = Progress
        fields = ['member', 'weight', 'remarks', 'updated_date']
        labels = {
            'weight': 'Weight (kg)',
            'remarks': 'Progress Remarks',
            'updated_date': 'Updated Date',
        }
        widgets = {
            'updated_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['updated_date'].initial = timezone.now().date()
        self.fields['bmi'].widget.attrs['readonly'] = True


class PaymentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['member', 'amount', 'payment_date', 'payment_method', 'payment_status']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['member'].queryset = Member.objects.order_by('fullname')
        self.fields['payment_date'].initial = timezone.now().date()
