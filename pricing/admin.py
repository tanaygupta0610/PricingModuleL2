from django.contrib import admin
from .models import (
    PricingConfig, DayOfWeekFactor, TimeBasedPrice,
    DistanceBasedPrice, WaitingCharge, BaseFare, Ride
)


class DayOfWeekFactorInline(admin.TabularInline):
    model = DayOfWeekFactor
    extra = 7
    max_num = 7


class TimeBasedPriceInline(admin.TabularInline):
    model = TimeBasedPrice
    extra = 1


class DistanceBasedPriceInline(admin.TabularInline):
    model = DistanceBasedPrice
    extra = 1


class WaitingChargeInline(admin.TabularInline):
    model = WaitingCharge
    extra = 1
    max_num = 1


class BaseFareInline(admin.TabularInline):
    model = BaseFare
    extra = 1
    max_num = 1


@admin.register(PricingConfig)
class PricingConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    inlines = [
        BaseFareInline,
        DayOfWeekFactorInline,
        TimeBasedPriceInline,
        DistanceBasedPriceInline,
        WaitingChargeInline,
    ]


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ('ride_date', 'distance', 'duration', 'waiting_time', 'total_price')
    list_filter = ('ride_date', 'pricing_config')
    search_fields = ('ride_date',)
    readonly_fields = ('total_price',)

    fieldsets = (
        (None, {
            'fields': ('pricing_config', 'ride_date')
        }),
        ('Ride Details', {
            'fields': ('distance', 'duration', 'waiting_time', 'total_price')
        }),
    )