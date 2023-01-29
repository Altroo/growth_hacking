from django.contrib import admin
from .models import Boutique, Produit, Particulier, ParticulierProduit
from django.contrib.admin import ModelAdmin


class CustomBoutiqueAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'category', 'city', 'phone', 'web_site', 'added_date')
    search_fields = ('pk', 'url', 'name', 'category', 'city', 'phone', 'web_site', 'long_description')
    date_hierarchy = 'added_date'
    ordering = ('-pk',)


class CustomProduitAdmin(ModelAdmin):
    list_display = ('pk', 'title', 'category', 'price', 'date_published')
    search_fields = ('pk', 'url', 'title', 'category', 'price', 'description')
    date_hierarchy = 'date_published'
    ordering = ('-pk',)


class CustomParticulierAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'city', 'phone', 'added_date')
    search_fields = ('pk', 'name', 'city', 'phone')
    date_hierarchy = 'added_date'
    ordering = ('-pk',)


class CustomParticulierProduitAdmin(ModelAdmin):
    list_display = ('pk', 'title', 'category', 'price', 'date_published')
    search_fields = ('pk', 'url', 'title', 'category', 'price', 'description')
    date_hierarchy = 'date_published'
    ordering = ('-pk',)


admin.site.register(Boutique, CustomBoutiqueAdmin)
admin.site.register(Produit, CustomProduitAdmin)
admin.site.register(Particulier, CustomParticulierAdmin)
admin.site.register(ParticulierProduit, CustomParticulierProduitAdmin)
