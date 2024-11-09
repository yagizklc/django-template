from django.db import models


class Organization(models.Model):
    """
    Holds organization information
    """

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
