from django.db import models
from django.conf import settings

# Create your models here.
class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
        )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.email



class BusinessCustomer(models.Model):
    business = models.ForeignKey(
        "businesses.Business", 
        on_delete=models.CASCADE,
        related_name="customers",
    )
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="businesses"
    )
    notes= models.TextField(
        blank=True, null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business","customer"],
                name = "unique_business_customer"
            )
        ]

    def __str__(self):
        return f"{self.customer} - {self.business.name}"