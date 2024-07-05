from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# form to manage guess submissions.
class GuessForm(forms.Form):
    current_image = forms.CharField(widget=forms.HiddenInput())
    correct_answer = forms.CharField(widget=forms.HiddenInput())
    guess = forms.CharField(label='Your Guess', max_length=100)


# form to create an account.
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
