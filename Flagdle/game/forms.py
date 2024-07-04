from django import forms

# form to manage guess submissions.
class GuessForm(forms.Form):
    current_image = forms.CharField(widget=forms.HiddenInput())
    correct_answer = forms.CharField(widget=forms.HiddenInput())
    guess = forms.CharField(label='Your Guess', max_length=100)
