from django import forms


class CheckoutForm(forms.Form):
    address = forms.CharField(label='Адрес доставки', widget=forms.Textarea(attrs={'rows': 3}))
    phone = forms.CharField(label='Телефон', max_length=20)
    email = forms.EmailField(label='Email')
    comment = forms.CharField(label='Комментарий к заказу', required=False, widget=forms.Textarea(attrs={'rows': 2}))

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    full_name = forms.CharField(max_length=200, required=False, label='Полное имя')
    phone = forms.CharField(max_length=20, required=False, label='Телефон')
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False, label='Адрес')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            user.profile.full_name = self.cleaned_data.get('full_name', '')
            user.profile.phone = self.cleaned_data.get('phone', '')
            user.profile.address = self.cleaned_data.get('address', '')
            user.profile.save()
        return user


class ProfileEditForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = Profile
        fields = ['full_name', 'phone', 'address', 'favorite_category', 'delivery_city']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.user.email = self.cleaned_data['email']
            profile.user.save()
            profile.save()
        return profile