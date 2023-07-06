from modeltranslation.translator import register, TranslationOptions

from . import models


@register(models.Product)
class ProductTranslation(TranslationOptions):
    fields = (
        'name',
        'description',
    )


@register(models.Category)
class CategoryTranslation(TranslationOptions):
    fields = (
        'name',
        'short_name',
    )
