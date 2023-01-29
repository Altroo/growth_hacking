from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Mubawab, MubawabProduit


class CustomMubawabAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'country', 'city', 'phone', 'added_date')
    search_fields = ('pk', 'name', 'city', 'phone')
    date_hierarchy = 'added_date'
    ordering = ('-pk',)


class CustomMubawabProduitAdmin(ModelAdmin):
    list_display = ('pk', 'title', 'category', 'price', 'date_published')
    search_fields = ('pk', 'url', 'title', 'type_annonce', 'category', 'price', 'description')
    list_filter = ('type_annonce', )
    date_hierarchy = 'date_published'
    ordering = ('-pk',)


admin.site.register(Mubawab, CustomMubawabAdmin)
admin.site.register(MubawabProduit, CustomMubawabProduitAdmin)
