from django.db import models
from django.conf import settings
# Create your models here.

class Business(models.Model):
    name = models.CharField(max_length=150)          # 20 chars was too short
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    logo = models.ImageField(upload_to="business/logos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # auto_now updates on every save

    def __str__(self):
        return self.name



class BusinessMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"   # value, then human-readable label
        STAFF = "STAFF", "Staff"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="business_memberships",   # typo fixed
    )
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=10, choices=Role.choices)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "business"], name="unique_user_business_membership")
        ]

    def __str__(self):
        return f"{self.user.email} - {self.business.name} ({self.role})"