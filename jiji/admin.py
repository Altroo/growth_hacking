from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Jiji, JijiProduit


class CustomJijiAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'country', 'city', 'phone', 'added_date')
    search_fields = ('pk', 'name', 'city', 'phone')
    date_hierarchy = 'added_date'
    ordering = ('-pk',)


class CustomJijiProduitAdmin(ModelAdmin):
    list_display = ('pk', 'title', 'category', 'price', 'date_published')
    search_fields = ('pk', 'url', 'title', 'category', 'price', 'description')
    date_hierarchy = 'date_published'
    ordering = ('-pk',)


admin.site.register(Jiji, CustomJijiAdmin)
admin.site.register(JijiProduit, CustomJijiProduitAdmin)
