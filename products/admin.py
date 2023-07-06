from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from modeltranslation.admin import TranslationAdmin

from . import models


class CategoryFilter(SimpleListFilter):
    title = _('Category')
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        categories = models.Category.objects.all()
        return [(category.id, category.name) for category in categories]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(category__id=value)
        return queryset


@admin.register(models.Product)
class ProductAdmin(TranslationAdmin):
    list_display = ('id', 'name', 'regular_price', 'category')
    list_filter = (CategoryFilter,)
    search_fields = ('name',)


class CategorySearchFilter(SimpleListFilter):
    title = _('Search by Category')
    parameter_name = 'category_search'

    def lookups(self, request, model_admin):
        return []

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(
                Q(name__icontains=value) |
                Q(short_name__icontains=value)
            )
        return queryset


@admin.register(models.Category)
class CategoryAdmin(TranslationAdmin):
    list_display = (
        'id',
        'name',
        'short_name',
        'is_active',
        'parent',
    )
    list_filter = (CategorySearchFilter,)
    search_fields = ('name', 'short_name',)
