from django.contrib import admin
from .models import Testator, Beneficiary, Asset, Will, AssetDistribution, DeathCertificate


admin.site.register(Beneficiary)
admin.site.register(Asset)
admin.site.register(Will)
admin.site.register(AssetDistribution)
admin.site.register(DeathCertificate)
from django.contrib import admin
from .models import Testator

from django.contrib import admin
from .models import Testator
from django.contrib import admin
from .models import Testator

@admin.register(Testator)
class TestatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'aadhaar')
def save_model(self, request, obj, form, change):
    # REMOVE SPACES
    obj.aadhaar = obj.aadhaar.replace(" ", "")

    if len(obj.aadhaar) != 12 or not obj.aadhaar.isdigit():
        raise ValueError("Aadhaar must be exactly 12 digits")

    super().save_model(request, obj, form, change)