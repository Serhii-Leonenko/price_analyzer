from django.db.models import TextChoices


class TrendChoices(TextChoices):
    UP = "up"
    STABLE = "stable"
    DOWN = "down"
    UNKNOWN = "unknown"
