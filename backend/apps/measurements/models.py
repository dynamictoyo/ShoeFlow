from django.db import models

# Create your models here.


class MeasurementType(models.Model):
    business= models.ForeignKey("businesses.Business", on_delete=models.CASCADE, related_name="measurement_types")
    name=models.CharField(max_length=100)
    unit=models.CharField(max_length=20, default="cm")
    description=models.TextField(blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            # Stops a shoemaker creating "Foot Length" twice
            models.UniqueConstraint(fields=["business", "name"], name="unique_measurement_type_per_business")
        ]


    def __str__(self):
        return f"{self.business.name} - {self.name}"

class CustomerMeasurement(models.Model):
    class MeasurementMethod(models.TextChoices):
        MANUAL = "MANUAL", "Manual"
        CUSTOMER_REPORTED = "CUSTOMER_REPORTED", "Customer Reported"
        REMOTE = "REMOTE", "Remote"

    # Anchored to the junction, not the raw customer profile:
    # a measurement now unambiguously belongs to ONE business relationship.
    business_customer = models.ForeignKey(
        "customers.BusinessCustomer",
        on_delete=models.CASCADE,
        related_name="measurements",
    )
    measurement_type = models.ForeignKey(
        MeasurementType,
        on_delete=models.PROTECT,   # can't delete a type that history depends on
        related_name="customer_measurements",
    )
    value = models.DecimalField(max_digits=6, decimal_places=2)
    measurement_method = models.CharField(
        max_length=30, choices=MeasurementMethod.choices, default=MeasurementMethod.MANUAL
    )
    is_verified = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Model-level guard: type must belong to the same business
        if self.measurement_type.business_id != self.business_customer.business_id:
            raise ValidationError("Measurement type does not belong to this business.")

    def __str__(self):
        return f"{self.business_customer.customer} - {self.measurement_type.name}: {self.value}"

class OrderMeasurement(models.Model):
    # A SNAPSHOT: copied onto the order at creation time.
    # If the customer's foot changes later, the order keeps what it was built to.
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="measurements")
    measurement_type = models.ForeignKey(
        MeasurementType, on_delete=models.PROTECT, related_name="order_measurements"
    )
    value = models.DecimalField(max_digits=6, decimal_places=2)
    unit = models.CharField(max_length=20)   # snapshot the unit too
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.measurement_type.name}: {self.value}"