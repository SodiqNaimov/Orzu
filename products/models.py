from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.models import BaseModel


class SortableModel(BaseModel):
    ordering = models.PositiveIntegerField(_("ordering"), default=0)

    class Meta:
        abstract = True


class Category(SortableModel):
    name = models.CharField(_('name'), max_length=255)
    short_name = models.CharField(_("short name"), max_length=100)
    is_active = models.BooleanField(_("is active"), default=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('-id',)
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def get_categories(self):
        if self.parent is None:
            return self.name
        return self.parent.name + ' -> ' + self.name

    def __str__(self):
        return self.get_categories()


class Product(SortableModel):
    UPLOAD_TO = "images/%Y/%m/%d/"

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), null=True, blank=True)
    is_active = models.BooleanField(_("is active"), default=True)
    regular_price = models.DecimalField(_("regular price"), max_digits=20, decimal_places=2)
    image = models.ImageField(upload_to=UPLOAD_TO)

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ('ordering', '-id')

    def __str__(self):
        return self.name
