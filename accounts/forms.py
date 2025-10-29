from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import User, Country, State, District

class LoginForm(forms.Form):
    username = forms.CharField(
        widget= forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )

class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True
    )
    state = forms.ModelChoiceField(
        queryset=State.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True
    )
    passkey = forms.CharField(
    required=False,
    widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )


    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'is_manager', 'is_trainer', 'is_student','country', 'state', 'district', 'passkey')
        
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['state'].queryset = State.objects.none()
        self.fields['district'].queryset = District.objects.none()

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['state'].queryset = State.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass

        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['district'].queryset = District.objects.filter(state_id=state_id).order_by('name')
            except (ValueError, TypeError):
                pass


from django import forms
from .models import StudentProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['profile_pic', 'bio']

class StudentUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name', 'last_name', 'email']

