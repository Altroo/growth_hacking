from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import MarocAnnonce, MarocAnnonceProduit


class CustomMarocAnnonceAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'country', 'city', 'phone', 'added_date')
    search_fields = ('pk', 'name', 'city', 'phone')
    date_hierarchy = 'added_date'
    ordering = ('-pk',)


class CustomMarocAnnonceProduitAdmin(ModelAdmin):
    list_display = ('pk', 'title', 'category', 'price', 'date_published')
    search_fields = ('pk', 'url', 'title', 'category', 'price', 'description')
    list_filter = ('category', )
    date_hierarchy = 'date_published'
    ordering = ('-pk',)


admin.site.register(MarocAnnonce, CustomMarocAnnonceAdmin)
admin.site.register(MarocAnnonceProduit, CustomMarocAnnonceProduitAdmin)
