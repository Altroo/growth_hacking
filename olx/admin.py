from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Olx, OlxProduit


class CustomOlxAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'city', 'phone', 'added_date')
    search_fields = ('pk', 'name', 'city', 'phone')
    date_hierarchy = 'added_date'
    ordering = ('-pk',)


class CustomOlxProduitAdmin(ModelAdmin):
    list_display = ('pk', 'title', 'category', 'price', 'date_published')
    search_fields = ('pk', 'url', 'title', 'category', 'price', 'description')
    date_hierarchy = 'date_published'
    ordering = ('-pk',)


admin.site.register(Olx, CustomOlxAdmin)
admin.site.register(OlxProduit, CustomOlxProduitAdmin)
