from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerProfile

class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label='Name', max_length=100, required=True)
    email = forms.EmailField(required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    pincode = forms.CharField(max_length=10, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'email')

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if pincode != '607106':
            raise forms.ValidationError("Service is currently only available for pincode 607106.")
        return pincode

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            CustomerProfile.objects.create(
                user=user,
                address=self.cleaned_data['address'],
                phone_number=self.cleaned_data['phone_number'],
                pincode=self.cleaned_data['pincode']
            )
        return user
