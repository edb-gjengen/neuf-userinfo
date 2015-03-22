from django.contrib import admin
from neuf_radius.models import Radcheck


class RadcheckAdmin(admin.ModelAdmin):
    search_fields = ['username']

admin.site.register(Radcheck, RadcheckAdmin)