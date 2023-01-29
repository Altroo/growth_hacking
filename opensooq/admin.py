from django.contrib import admin
from .models import OpenSooqBoutique, OpenSooqBoutiqueProduit, OpenSooqParticulier, OpenSooqParticulierProduit
from django.contrib.admin import ModelAdmin


class CustomOpenSooqBoutiqueAdmin(ModelAdmin):
    list_display = ('pk', 'country', 'name', 'category', 'city', 'phone', 'added_date')
    search_fields = ('pk', 'url', 'country', 'name', 'category', 'city', 'phone', 'description')
    list_filter = ('country',)
    date_hierarchy = 'added_date'
    ordering = ('-pk',)


class CustomOpenSooqBoutiqueProduitAdmin(ModelAdmin):
    list_display = ('pk', 'title', 'category', 'price', 'date_published')
    search_fields = ('pk', 'url', 'title', 'category', 'price', 'description')
    date_hierarchy = 'date_published'
    ordering = ('-pk',)


class CustomOpenSooqParticulierAdmin(ModelAdmin):
    list_display = ('pk', 'country', 'name', 'city', 'phone', 'added_date')
    search_fields = ('pk', 'country', 'name', 'city', 'phone')
    list_filter = ('country',)
    date_hierarchy = 'added_date'
    ordering = ('-pk',)


class CustomOpenSooqParticulierProduitAdmin(ModelAdmin):
    list_display = ('pk', 'title', 'category', 'price', 'date_published')
    search_fields = ('pk', 'url', 'title', 'category', 'price', 'description')
    date_hierarchy = 'date_published'
    ordering = ('-pk',)


admin.site.register(OpenSooqBoutique, CustomOpenSooqBoutiqueAdmin)
admin.site.register(OpenSooqBoutiqueProduit, CustomOpenSooqBoutiqueProduitAdmin)
admin.site.register(OpenSooqParticulier, CustomOpenSooqParticulierAdmin)
admin.site.register(OpenSooqParticulierProduit, CustomOpenSooqParticulierProduitAdmin)
