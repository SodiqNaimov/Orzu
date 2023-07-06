from django.db.models import TextChoices


class UserType(TextChoices):
    SUPER_USER = 'super_user'
    CUSTOMER = 'customer'
