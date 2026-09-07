from django.db import models
from django.db.models import DecimalField, ExpressionWrapper, F, Sum

# Create your models here.
class Order(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PRODUCTION = "IN PRODUCTION", "In Production"
        READY = "READY", "Ready"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    business = models.ForeignKey(
        "businesses.Business", on_delete=models.CASCADE, related_name="orders"
    )
    customer = models.ForeignKey(
        "customers.CustomerProfile", on_delete=models.CASCADE, related_name="orders"
    )
    order_number = models.CharField(max_length=30, unique=True)
    design_name = models.CharField(
        max_length=200,
    )
    design_Image = models.ImageField(
        upload_to="orders/designs/",
        blank=True,
        null=True,
    )
    notes = models.TextField(
        blank=True,
        null=True,
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    expected_delivery_date = models.DateField(
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def update_total(self):
        total = OrderItem.objects.filter(
            order=self
        ).aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("quantity") * F("unit_price"),
                    output_field=DecimalField(
                        max_digits=12,
                        decimal_places=2,
                    ),
                )
            )
        )["total"]

        self.total_amount = total or 0
        self.save(update_fields=["total_amount"])

    def __str__(self):
        return f"{self.order_number} - {self.customer}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    size = models.DecimalField(max_digits=4, decimal_places=1)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.order.order_number} - Size {self.size}"
