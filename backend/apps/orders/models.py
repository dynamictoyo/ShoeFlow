from decimal import Decimal
from uuid import uuid4

from django.db import models
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.utils import timezone


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PRODUCTION = "IN_PRODUCTION", "In Production"
        READY = "READY", "Ready"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    # Anchored to the junction — the DB itself now rejects an order
    # for a customer who doesn't belong to this business.
    # PROTECT: you cannot delete a customer link that has order history.
    business_customer = models.ForeignKey(
        "customers.BusinessCustomer",
        on_delete=models.PROTECT,
        related_name="orders",
    )
    order_number = models.CharField(max_length=30, unique=True, blank=True)
    notes = models.TextField(blank=True)
    # Denormalized cache of the item sum. editable=False so no form/API
    # can ever write it directly — only update_total() may change it.
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, editable=False
    )
    expected_delivery_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def _generate_order_number(self):
        # Human-readable + unique: SF-20260911-4F2A9C
        return f"SF-{timezone.now():%Y%m%d}-{uuid4().hex[:6].upper()}"

    def update_total(self):
        result = self.items.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("quantity") * F("unit_price"),
                    output_field=DecimalField(max_digits=14, decimal_places=2),
                )
            )
        )["total"]
        total = result or Decimal("0.00")
        # QuerySet.update(): no signals, no recursion, atomic write
        Order.objects.filter(pk=self.pk).update(total_amount=total)
        self.total_amount = total

    def __str__(self):
        return f"{self.order_number} - {self.business_customer.customer}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    # Nullable: bespoke orders may have no catalogue product.
    # SET_NULL keeps the item (and its price history) if a product is deleted.
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    design_name = models.CharField(max_length=200, blank=True)  # moved from Order
    size = models.DecimalField(max_digits=4, decimal_places=1)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)  # snapshot at order time
    notes = models.TextField(blank=True)

    @property
    def total_price(self):
        return (self.quantity * self.unit_price).quantize(Decimal("0.01"))

    def __str__(self):
        return f"{self.order.order_number} - Size {self.size}"