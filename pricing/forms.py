from django import forms
from django.core.exceptions import ValidationError
from .models import PricingConfig, DayOfWeekFactor, TimeBasedPrice, DistanceBasedPrice, WaitingCharge, BaseFare


class PricingConfigForm(forms.ModelForm):
    class Meta:
        model = PricingConfig
        fields = ['name', 'is_active']

    def clean_name(self):
        name = self.cleaned_data['name']
        if PricingConfig.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A pricing configuration with this name already exists.")
        return name


class DayOfWeekFactorForm(forms.ModelForm):
    class Meta:
        model = DayOfWeekFactor
        fields = ['day', 'multiplier']

    def clean_multiplier(self):
        multiplier = self.cleaned_data['multiplier']
        if multiplier <= 0:
            raise ValidationError("Multiplier must be greater than 0.")
        return multiplier


class TimeBasedPriceForm(forms.ModelForm):
    class Meta:
        model = TimeBasedPrice
        fields = ['min_duration', 'max_duration', 'price_per_minute']

    def clean(self):
        cleaned_data = super().clean()
        min_duration = cleaned_data.get('min_duration')
        max_duration = cleaned_data.get('max_duration')

        if min_duration and max_duration and min_duration >= max_duration:
            raise ValidationError("Minimum duration must be less than maximum duration.")

        if min_duration and min_duration < 0:
            raise ValidationError("Duration cannot be negative.")

        if 'price_per_minute' in cleaned_data and cleaned_data['price_per_minute'] < 0:
            raise ValidationError("Price per minute cannot be negative.")

        return cleaned_data


class DistanceBasedPriceForm(forms.ModelForm):
    class Meta:
        model = DistanceBasedPrice
        fields = ['min_distance', 'max_distance', 'price_per_km']

    def clean(self):
        cleaned_data = super().clean()
        min_distance = cleaned_data.get('min_distance')
        max_distance = cleaned_data.get('max_distance')

        if min_distance and max_distance and min_distance >= max_distance:
            raise ValidationError("Minimum distance must be less than maximum distance.")

        if min_distance and min_distance < 0:
            raise ValidationError("Distance cannot be negative.")

        if 'price_per_km' in cleaned_data and cleaned_data['price_per_km'] < 0:
            raise ValidationError("Price per km cannot be negative.")

        return cleaned_data


class WaitingChargeForm(forms.ModelForm):
    class Meta:
        model = WaitingCharge
        fields = ['free_waiting_minutes', 'price_per_minute']

    def clean(self):
        cleaned_data = super().clean()

        if 'free_waiting_minutes' in cleaned_data and cleaned_data['free_waiting_minutes'] < 0:
            raise ValidationError("Free waiting minutes cannot be negative.")

        if 'price_per_minute' in cleaned_data and cleaned_data['price_per_minute'] < 0:
            raise ValidationError("Price per minute cannot be negative.")

        return cleaned_data


class BaseFareForm(forms.ModelForm):
    class Meta:
        model = BaseFare
        fields = ['amount']

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount < 0:
            raise ValidationError("Base fare cannot be negative.")