from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerProfile, AllowedPincode

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
        allowed = list(AllowedPincode.objects.filter(is_active=True).values_list('pincode', flat=True))
        if pincode not in allowed:
            raise forms.ValidationError(f"Service is currently only available for pincodes: {', '.join(allowed)}")
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

class ProfileUpdateForm(forms.Form):
    first_name = forms.CharField(label='Name', max_length=100, required=True)
    email = forms.EmailField(required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    pincode = forms.CharField(max_length=10, required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['email'].initial = self.user.email
            if hasattr(self.user, 'profile'):
                self.fields['address'].initial = self.user.profile.address
                self.fields['phone_number'].initial = self.user.profile.phone_number
                self.fields['pincode'].initial = self.user.profile.pincode

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        allowed = list(AllowedPincode.objects.filter(is_active=True).values_list('pincode', flat=True))
        if pincode not in allowed:
            raise forms.ValidationError(f"Service is currently only available for pincodes: {', '.join(allowed)}")
        return pincode

    def save(self):
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.email = self.cleaned_data['email']
            self.user.save()

            profile, created = CustomerProfile.objects.get_or_create(user=self.user)
            profile.address = self.cleaned_data['address']
            profile.phone_number = self.cleaned_data['phone_number']
            profile.pincode = self.cleaned_data['pincode']
            profile.save()
            return self.user
