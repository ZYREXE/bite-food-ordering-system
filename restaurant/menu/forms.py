from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


# registration 

class Userregistration(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


# login
class Loginform(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-field'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input-field'})
    )



# username and pass change
class UsernameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']