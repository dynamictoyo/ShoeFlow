from django.db import models

# Create your models here.


class MeasurementType(models.Model):
    business= models.ForeignKey("businesses.Business", on_delete=models.CASCADE, related_name="measurement_types")
    name=models.CharField(max_length=100)
    unit=models.CharField(max_length=20, default="cm")
    description=models.TextField(blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.business.name} - {self.name}"

class CustomerMeasurement(models.Model):

    class MeasurementMethod(models.TextChoices):
        MANUAL = "MANUAL", "Manual"
        CUSTOMER_REPORTED = "CUSTOMER_REPORTED", "Customer Reported"
        REMOTE = "REMOTE", "Remote"

    customer= models.ForeignKey("customers.CustomerProfile", on_delete=models.CASCADE, related_name="measurements")
    measurement_type = models.ForeignKey(MeasurementType, on_delete=models.PROTECT, related_name="customer_measurements",)
    value = models.DecimalField(max_digits=6, decimal_places=2)
    measurement_method = models.CharField(max_length=30, choices=MeasurementMethod.choices, default=MeasurementMethod.MANUAL)
    is_verified = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer} - {self.measurement_type.name}: {self.value}"

class OrderMeasurement(models.Model):

    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="measurements")
    measurement_type = models.ForeignKey(MeasurementType, on_delete=models.PROTECT, related_name="order_measurements")
    value=models.DecimalField(max_digits=6, decimal_places=2)
    notes = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.order.order_number} - {self.measurement_type.name}: {self.value}"