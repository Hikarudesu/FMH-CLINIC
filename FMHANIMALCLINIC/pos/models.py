"""
POS (Point of Sale) models for handling sales transactions.

Billable items include:
- Services (Service from billing app)
- Products (Product with item_type='Product' from inventory app)
- Medications (Product with item_type='Medication' from inventory app)
"""

import uuid
from decimal import Decimal

from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator

from branches.models import Branch
from billing.models import Service
from inventory.models import Product, StockAdjustment
from patients.models import Pet


class Sale(models.Model):
    """
    Represents a completed sale transaction.
    Links to customer (via Pet owner or guest info) and branch.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        VOIDED = 'VOIDED', 'Voided'
        REFUNDED = 'REFUNDED', 'Refunded'

    class CustomerType(models.TextChoices):
        REGISTERED = 'REGISTERED', 'Registered Customer'
        WALKIN = 'WALKIN', 'Walk-in Customer'

    # Transaction ID
    transaction_id = models.CharField(
        max_length=20, unique=True, editable=False,
        help_text='Auto-generated transaction ID')

    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name='sales')

    # Customer info - either linked to a registered user or guest info
    customer_type = models.CharField(
        max_length=15, choices=CustomerType.choices, default=CustomerType.WALKIN)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='purchases',
        help_text='Linked customer account (if registered)')
    pet = models.ForeignKey(
        Pet, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='sales', help_text='Pet receiving services (optional)')

    # Guest customer info (when customer is null)
    guest_name = models.CharField(max_length=200, blank=True)
    guest_phone = models.CharField(max_length=20, blank=True)
    guest_email = models.EmailField(blank=True)

    # Financial totals
    subtotal = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_reason = models.CharField(max_length=200, blank=True)
    tax_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Payment tracking
    amount_paid = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'))
    change_due = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'))

    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.PENDING)

    # Staff
    cashier = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='processed_sales')
    voided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='voided_sales')
    void_reason = models.CharField(max_length=200, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sale'
        verbose_name_plural = 'Sales'
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['branch', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"Sale {self.transaction_id}"

    def save(self, *args, **kwargs):
        """Auto-generate transaction ID if not set."""
        if not self.transaction_id:
            date_str = timezone.now().strftime('%Y%m%d')
            unique_part = str(uuid.uuid4())[:6].upper()
            self.transaction_id = f"TXN{date_str}{unique_part}"
        super().save(*args, **kwargs)

    def calculate_totals(self):
        """Recalculate totals from line items."""
        # CRITICAL: Refresh discount_amount from DB to prevent stale object from wiping it
        self.refresh_from_db(fields=['discount_amount', 'tax_amount'])

        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        self.total = self.subtotal - self.discount_amount + self.tax_amount
        # Only save computed fields - do NOT save discount_amount (it's user input, not computed)
        self.save(update_fields=['subtotal', 'total'])

    def complete_sale(self):
        """Mark sale as completed and deduct inventory."""
        if self.status != self.Status.PENDING:
            raise ValueError("Only pending sales can be completed.")

        with transaction.atomic():
            # Deduct inventory for product items
            for item in self.items.filter(item_type__in=['PRODUCT', 'MEDICATION']):
                if item.product:
                    StockAdjustment.objects.create(
                        branch=self.branch,
                        product=item.product,
                        adjustment_type='Sale',
                        reference=self.transaction_id,
                        date=timezone.now().date(),
                        quantity=item.quantity,
                        cost_per_unit=item.product.unit_cost,
                        reason=f"POS Sale {self.transaction_id}"
                    )

            self.status = self.Status.COMPLETED
            self.completed_at = timezone.now()
            self.save(update_fields=['status', 'completed_at'])

    def void_sale(self, user, reason=''):
        """Void the sale and restore inventory if already completed."""
        if self.status == self.Status.VOIDED:
            raise ValueError("Sale is already voided.")

        with transaction.atomic():
            # Restore inventory if sale was completed
            if self.status == self.Status.COMPLETED:
                for item in self.items.filter(item_type__in=['PRODUCT', 'MEDICATION']):
                    if item.product:
                        StockAdjustment.objects.create(
                            branch=self.branch,
                            product=item.product,
                            adjustment_type='Return',
                            reference=f"VOID-{self.transaction_id}",
                            date=timezone.now().date(),
                            quantity=item.quantity,
                            cost_per_unit=item.product.unit_cost,
                            reason=f"Voided sale {self.transaction_id}: {reason}"
                        )

            self.status = self.Status.VOIDED
            self.voided_by = user
            self.void_reason = reason
            self.save(update_fields=['status', 'voided_by', 'void_reason'])

    @property
    def customer_display_name(self):
        """Return the customer's display name."""
        if self.customer:
            return self.customer.get_full_name() or self.customer.email
        return self.guest_name or "Walk-in Customer"

    @property
    def balance_due(self):
        """Calculate remaining balance."""
        return max(Decimal('0.00'), self.total - self.amount_paid)

    @property
    def is_fully_paid(self):
        """Check if sale is fully paid."""
        return self.amount_paid >= self.total


class SaleItem(models.Model):
    """
    A line item in a sale - can be a service, product, or medication.
    """

    class ItemType(models.TextChoices):
        SERVICE = 'SERVICE', 'Service'
        PRODUCT = 'PRODUCT', 'Product'
        MEDICATION = 'MEDICATION', 'Medication'

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')

    item_type = models.CharField(max_length=15, choices=ItemType.choices)

    # References to actual items (one will be set based on item_type)
    service = models.ForeignKey(
        Service, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='sale_items')
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='sale_items')

    # Snapshot of item details at time of sale
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    # Line item discount
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'))

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Sale Item'
        verbose_name_plural = 'Sale Items'

    def __str__(self):
        return f"{self.quantity}x {self.name}"

    @property
    def line_total(self):
        """Calculate line total after discount."""
        return (self.unit_price * self.quantity) - self.discount

    def save(self, *args, **kwargs):
        """Populate name and unit_price from the referenced item if not set."""
        if self.item_type == self.ItemType.SERVICE and self.service:
            if not self.name:
                self.name = self.service.name
            if not self.unit_price:
                self.unit_price = self.service.price
        elif self.item_type in [self.ItemType.PRODUCT, self.ItemType.MEDICATION] and self.product:
            if not self.name:
                self.name = self.product.name
            if not self.unit_price:
                self.unit_price = self.product.price

        super().save(*args, **kwargs)

        # Recalculate sale totals
        if self.sale_id:
            self.sale.calculate_totals()


class Payment(models.Model):
    """
    Payment record for a sale. Supports split payments across multiple methods.
    """

    class Method(models.TextChoices):
        CASH = 'CASH', 'Cash'
        CARD = 'CARD', 'Credit/Debit Card'
        GCASH = 'GCASH', 'GCash'
        MAYA = 'MAYA', 'Maya/PayMaya'
        BANK = 'BANK', 'Bank Transfer'
        OTHER = 'OTHER', 'Other'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments')

    method = models.CharField(max_length=10, choices=Method.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.COMPLETED)

    # Payment details
    reference_number = models.CharField(
        max_length=100, blank=True,
        help_text='Card last 4 digits, GCash ref#, etc.')
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='received_payments')

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"{self.get_method_display()} - ₱{self.amount}"

    def save(self, *args, **kwargs):
        """Update sale's amount_paid and change_due after payment."""
        super().save(*args, **kwargs)

        if self.sale_id and self.status == self.Status.COMPLETED:
            total_paid = self.sale.payments.filter(
                status=self.Status.COMPLETED
            ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

            self.sale.amount_paid = total_paid
            self.sale.change_due = max(Decimal('0.00'), total_paid - self.sale.total)
            self.sale.save(update_fields=['amount_paid', 'change_due'])


class Refund(models.Model):
    """
    Refund record for a sale or specific items.
    """

    class RefundType(models.TextChoices):
        FULL = 'FULL', 'Full Refund'
        PARTIAL = 'PARTIAL', 'Partial Refund'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        COMPLETED = 'COMPLETED', 'Completed'
        REJECTED = 'REJECTED', 'Rejected'

    refund_id = models.CharField(
        max_length=20, unique=True, editable=False,
        help_text='Auto-generated refund ID')

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='refunds')
    refund_type = models.CharField(
        max_length=10, choices=RefundType.choices, default=RefundType.FULL)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()

    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.PENDING)

    # Staff involved
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='requested_refunds')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='approved_refunds')
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='processed_refunds')

    # Refund method
    refund_method = models.CharField(
        max_length=10, choices=Payment.Method.choices, default=Payment.Method.CASH)
    reference_number = models.CharField(max_length=100, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'

    def __str__(self):
        return f"Refund {self.refund_id} - ₱{self.amount}"

    def save(self, *args, **kwargs):
        """Auto-generate refund ID if not set."""
        if not self.refund_id:
            date_str = timezone.now().strftime('%Y%m%d')
            unique_part = str(uuid.uuid4())[:6].upper()
            self.refund_id = f"REF{date_str}{unique_part}"
        super().save(*args, **kwargs)

    def complete_refund(self, user):
        """Complete the refund and update sale status."""
        if self.status != self.Status.APPROVED:
            raise ValueError("Only approved refunds can be completed.")

        with transaction.atomic():
            # Restore inventory for refunded product items
            for item in self.items.filter(
                sale_item__item_type__in=['PRODUCT', 'MEDICATION']
            ):
                if item.sale_item.product:
                    StockAdjustment.objects.create(
                        branch=self.sale.branch,
                        product=item.sale_item.product,
                        adjustment_type='Return',
                        reference=self.refund_id,
                        date=timezone.now().date(),
                        quantity=item.quantity,
                        cost_per_unit=item.sale_item.product.unit_cost,
                        reason=f"Refund {self.refund_id}: {self.reason}"
                    )

            self.status = self.Status.COMPLETED
            self.processed_by = user
            self.completed_at = timezone.now()
            self.save()

            # Update sale status if full refund
            if self.refund_type == self.RefundType.FULL:
                self.sale.status = Sale.Status.REFUNDED
                self.sale.save(update_fields=['status'])


class RefundItem(models.Model):
    """
    Specific items being refunded (for partial refunds).
    """

    refund = models.ForeignKey(Refund, on_delete=models.CASCADE, related_name='items')
    sale_item = models.ForeignKey(
        SaleItem, on_delete=models.CASCADE, related_name='refund_items')
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Refund Item'
        verbose_name_plural = 'Refund Items'

    def __str__(self):
        return f"{self.quantity}x {self.sale_item.name}"
