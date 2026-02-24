from django.db.models import TextChoices


class StoreChoices(TextChoices):
    DUMMYJSON = "dummyjson"
    FAKESTORE = "fakestore"
