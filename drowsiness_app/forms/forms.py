from django import forms
from django.contrib.auth.forms import UserCreationForm
from ..models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "password1", "password2", "user_role")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")
        return password2
