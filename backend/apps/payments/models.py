from django.db import models

from apps.core.models import SoftDeleteModel


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"
    CANCELLED = "cancelled", "Cancelled"


class PaymentMethod(models.TextChoices):
    CASH = "cash", "Cash"
    CARD = "card", "Card"
    UPI = "upi", "UPI"
    INSURANCE = "insurance", "Insurance"
    OTHER = "other", "Other"


class Payment(SoftDeleteModel):
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
    )
    payment_date = models.DateField(db_index=True)
    method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
    )
    reference = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "payments"
        ordering = ["-payment_date"]
        indexes = [
            models.Index(fields=["patient", "status"]),
        ]

    def __str__(self):
        return f"{self.patient} — {self.amount}"
