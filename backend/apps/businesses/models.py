from django.db import models
from django.conf import settings
# Create your models here.

class Business(models.Model):
    name= models.CharField(max_length=20, blank=True, null=True)
    email=models.EmailField(blank=True, null=True)
    address=models.TextField(blank=True, null=True)
    logo=models.ImageField(upload_to="business/logos/", blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):  # type: ignore
        return self.name


class BusinessMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "Owner", "owner"
        STAFF = "Staff", "staff"

    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="business_membersip")
    business=models.ForeignKey(Business, on_delete=models.CASCADE, related_name="memberships",)
    role=models.CharField(max_length=20, choices=Role.choices,)
    joined_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "business"],
                name="unique_user_business_membership",
            )
        ]


    def __str__(self):
        return f"{self.user.email} - {self.business.name} ({self.role})"