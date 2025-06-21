from django.db import models
from django.core.validators import MinValueValidator


class PricingConfig(models.Model):
    """Main configuration that holds pricing rules"""
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"


class DayOfWeekFactor(models.Model):
    """Multipliers for different days of the week"""
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    pricing_config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE, related_name='day_factors')
    day = models.IntegerField(choices=DAY_CHOICES)
    multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)

    class Meta:
        unique_together = ('pricing_config', 'day')

    def __str__(self):
        return f"{self.get_day_display()}: {self.multiplier}x"


class TimeBasedPrice(models.Model):
    """Pricing based on time duration of the ride"""
    pricing_config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE, related_name='time_prices')
    min_duration = models.PositiveIntegerField(help_text="Minimum duration in minutes")  # in minutes
    max_duration = models.PositiveIntegerField(help_text="Maximum duration in minutes")  # in minutes
    price_per_minute = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ['min_duration']

    def __str__(self):
        return f"{self.min_duration}-{self.max_duration} mins: ${self.price_per_minute}/min"


class DistanceBasedPrice(models.Model):
    """Pricing based on distance traveled"""
    pricing_config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE, related_name='distance_prices')
    min_distance = models.PositiveIntegerField(help_text="Minimum distance in kilometers")  # in km
    max_distance = models.PositiveIntegerField(help_text="Maximum distance in kilometers")  # in km
    price_per_km = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ['min_distance']

    def __str__(self):
        return f"{self.min_distance}-{self.max_distance} km: ${self.price_per_km}/km"


class WaitingCharge(models.Model):
    """Charges for waiting time"""
    pricing_config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE, related_name='waiting_charges')
    free_waiting_minutes = models.PositiveIntegerField(default=3, help_text="Free waiting time in minutes")
    price_per_minute = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"After {self.free_waiting_minutes} mins: ${self.price_per_minute}/min"


class BaseFare(models.Model):
    """Initial fixed charge for a ride"""
    pricing_config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE, related_name='base_fares')
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"Base fare: ${self.amount}"


class Ride(models.Model):
    """Example ride model to demonstrate pricing calculation"""
    pricing_config = models.ForeignKey(PricingConfig, on_delete=models.SET_NULL, null=True)
    distance = models.DecimalField(max_digits=6, decimal_places=2, help_text="Distance in kilometers")
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    waiting_time = models.PositiveIntegerField(help_text="Waiting time in minutes")
    ride_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_price(self):
        if not self.pricing_config:
            return 0

        # Get day of week (0=Monday, 6=Sunday)
        day_of_week = self.ride_date.weekday()

        try:
            day_factor = self.pricing_config.day_factors.get(day=day_of_week).multiplier
        except DayOfWeekFactor.DoesNotExist:
            day_factor = 1.0

        # Calculate distance price
        distance_price = 0
        distance_ranges = self.pricing_config.distance_prices.order_by('min_distance')
        remaining_distance = self.distance

        for range in distance_ranges:
            if remaining_distance <= 0:
                break
            applicable_distance = min(
                remaining_distance,
                range.max_distance - range.min_distance if range.max_distance else remaining_distance
            )
            distance_price += applicable_distance * float(range.price_per_km)
            remaining_distance -= applicable_distance

        # Calculate time price
        time_price = 0
        time_ranges = self.pricing_config.time_prices.order_by('min_duration')
        remaining_time = self.duration

        for range in time_ranges:
            if remaining_time <= 0:
                break
            applicable_time = min(
                remaining_time,
                range.max_duration - range.min_duration if range.max_duration else remaining_time
            )
            time_price += applicable_time * float(range.price_per_minute)
            remaining_time -= applicable_time

        # Calculate waiting charges
        waiting_charge = 0
        try:
            waiting_config = self.pricing_config.waiting_charges.first()
            if waiting_config and self.waiting_time > waiting_config.free_waiting_minutes:
                chargeable_waiting = self.waiting_time - waiting_config.free_waiting_minutes
                waiting_charge = chargeable_waiting * float(waiting_config.price_per_minute)
        except WaitingCharge.DoesNotExist:
            pass

        # Get base fare
        try:
            base_fare = float(self.pricing_config.base_fares.first().amount)
        except (BaseFare.DoesNotExist, AttributeError):
            base_fare = 0

        # Calculate total
        total = (base_fare + distance_price + time_price + waiting_charge) * day_factor
        return round(total, 2)

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.calculate_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ride on {self.ride_date} - {self.distance}km, {self.duration}min"