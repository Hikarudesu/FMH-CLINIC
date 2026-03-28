"""
Service layer for POS (Point of Sale) business logic.

This module contains the core business logic for sales management,
extracted from views for better separation of concerns and testability.
"""
import logging
from decimal import Decimal
from typing import Optional, Dict, List, Tuple

from django.db import transaction
from django.db.models import Q

from branches.models import Branch
from billing.models import Service
from inventory.models import Product
from patients.models import Pet
from accounts.models import User

from .models import CashDrawer, Sale, SaleItem, Payment

logger = logging.getLogger('fmh')


class POSServiceError(Exception):
    """Custom exception for POS service errors."""
    pass


class SaleService:
    """Service class for sale-related operations."""

    @staticmethod
    def get_or_create_pending_sale(branch: Branch, cashier: User) -> Sale:
        """
        Get existing pending sale or create a new one.
        
        Args:
            branch: The branch where the sale occurs.
            cashier: The user processing the sale.
            
        Returns:
            A pending Sale instance.
        """
        pending_sale = Sale.objects.filter(
            branch=branch,
            cashier=cashier,
            status=Sale.Status.PENDING
        ).first()

        if not pending_sale:
            pending_sale = Sale.objects.create(
                branch=branch,
                cashier=cashier
            )
            logger.info("Created new sale %s for cashier %s", 
                       pending_sale.transaction_id, cashier.pk)

        return pending_sale

    @staticmethod
    def add_service_item(
        sale: Sale,
        service_id: int,
        quantity: int = 1
    ) -> Tuple[SaleItem, bool]:
        """
        Add a service to the sale.
        
        Args:
            sale: The sale to add the item to.
            service_id: The service ID.
            quantity: Quantity to add.
            
        Returns:
            Tuple of (SaleItem, is_new) where is_new indicates if item was created.
            
        Raises:
            POSServiceError: If sale is not pending or service not found.
        """
        if sale.status != Sale.Status.PENDING:
            raise POSServiceError("Cannot add items to non-pending sale")

        try:
            service = Service.objects.get(pk=service_id, active=True)
        except Service.DoesNotExist:
            raise POSServiceError("Service not found or inactive")

        # Consolidate if exists
        existing_item = sale.items.filter(
            item_type=SaleItem.ItemType.SERVICE,
            service=service
        ).first()

        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
            logger.debug("Updated service item quantity in sale %s", sale.pk)
            return existing_item, False
        else:
            sale_item = SaleItem.objects.create(
                sale=sale,
                item_type=SaleItem.ItemType.SERVICE,
                service=service,
                name=service.name,
                unit_price=service.price,
                quantity=quantity
            )
            logger.debug("Added new service item to sale %s", sale.pk)
            return sale_item, True

    @staticmethod
    def add_product_item(
        sale: Sale,
        product_id: int,
        item_type: str,
        quantity: int = 1
    ) -> Tuple[SaleItem, bool]:
        """
        Add a product or medication to the sale.
        
        Args:
            sale: The sale to add the item to.
            product_id: The product ID.
            item_type: Either 'PRODUCT' or 'MEDICATION'.
            quantity: Quantity to add.
            
        Returns:
            Tuple of (SaleItem, is_new).
            
        Raises:
            POSServiceError: If sale is not pending, product not found, or insufficient stock.
        """
        if sale.status != Sale.Status.PENDING:
            raise POSServiceError("Cannot add items to non-pending sale")

        if item_type not in ['PRODUCT', 'MEDICATION']:
            raise POSServiceError("Invalid item type")

        try:
            product = Product.objects.get(pk=product_id, is_available=True)
        except Product.DoesNotExist:
            raise POSServiceError("Product not found or unavailable")

        # Check existing quantity
        existing_item = sale.items.filter(item_type=item_type, product=product).first()
        new_quantity = (existing_item.quantity if existing_item else 0) + quantity

        # Validate stock
        if product.stock_quantity < new_quantity:
            raise POSServiceError(
                f"Insufficient stock. Available: {product.stock_quantity}"
            )

        if existing_item:
            existing_item.quantity = new_quantity
            existing_item.save()
            logger.debug("Updated product item quantity in sale %s", sale.pk)
            return existing_item, False
        else:
            sale_item = SaleItem.objects.create(
                sale=sale,
                item_type=item_type,
                product=product,
                name=product.name,
                unit_price=product.price,
                quantity=quantity
            )
            logger.debug("Added new product item to sale %s", sale.pk)
            return sale_item, True

    @staticmethod
    def remove_item(sale: Sale, item_id: int) -> bool:
        """
        Remove an item from the sale.
        
        Args:
            sale: The sale to remove from.
            item_id: The SaleItem ID to remove.
            
        Returns:
            True if item was removed, False otherwise.
        """
        if sale.status != Sale.Status.PENDING:
            logger.warning("Attempted to remove item from non-pending sale %s", sale.pk)
            return False

        try:
            item = sale.items.get(pk=item_id)
            item.delete()
            sale.calculate_totals()
            logger.info("Removed item %s from sale %s", item_id, sale.pk)
            return True
        except SaleItem.DoesNotExist:
            return False

    @staticmethod
    def update_item_quantity(
        sale: Sale,
        item_id: int,
        quantity: int
    ) -> Optional[SaleItem]:
        """
        Update the quantity of a sale item.
        
        Args:
            sale: The sale containing the item.
            item_id: The SaleItem ID.
            quantity: New quantity (0 to remove).
            
        Returns:
            Updated SaleItem or None if removed/not found.
            
        Raises:
            POSServiceError: If insufficient stock.
        """
        if sale.status != Sale.Status.PENDING:
            raise POSServiceError("Cannot update items in non-pending sale")

        try:
            item = sale.items.get(pk=item_id)
        except SaleItem.DoesNotExist:
            return None

        if quantity <= 0:
            item.delete()
            sale.calculate_totals()
            return None

        # Check stock for products
        if item.product and item.product.stock_quantity < quantity:
            raise POSServiceError(
                f"Insufficient stock. Available: {item.product.stock_quantity}"
            )

        item.quantity = quantity
        item.save()
        sale.calculate_totals()
        return item

    @staticmethod
    def apply_discount(
        sale: Sale,
        amount: Decimal,
        reason: str = ''
    ) -> Sale:
        """
        Apply a discount to the sale.
        
        Args:
            sale: The sale to discount.
            amount: Discount amount.
            reason: Reason for discount.
            
        Returns:
            Updated sale instance.
        """
        if sale.status != Sale.Status.PENDING:
            raise POSServiceError("Cannot apply discount to non-pending sale")

        sale.discount_amount = amount
        sale.discount_reason = reason
        sale.save(update_fields=['discount_amount', 'discount_reason'])
        sale.calculate_totals()
        
        logger.info("Applied discount of %s to sale %s: %s", 
                   amount, sale.pk, reason)
        return sale

    @staticmethod
    def set_customer(
        sale: Sale,
        customer_id: Optional[int] = None,
        customer_type: str = 'WALKIN',
        guest_name: str = '',
        guest_phone: str = '',
        guest_email: str = '',
        pet_id: Optional[int] = None
    ) -> Sale:
        """
        Set customer information for the sale.
        
        Args:
            sale: The sale to update.
            customer_id: Optional registered customer ID.
            customer_type: 'REGISTERED' or 'WALKIN'.
            guest_name: Guest customer name.
            guest_phone: Guest phone number.
            guest_email: Guest email.
            pet_id: Optional pet ID.
            
        Returns:
            Updated sale instance.
        """
        sale.customer_type = customer_type

        if customer_id:
            try:
                sale.customer = User.objects.get(pk=customer_id)
                sale.customer_type = 'REGISTERED'
            except User.DoesNotExist:
                logger.warning("Customer %s not found", customer_id)

        sale.guest_name = guest_name
        sale.guest_phone = guest_phone
        sale.guest_email = guest_email

        if pet_id:
            try:
                sale.pet = Pet.objects.get(pk=pet_id)
            except Pet.DoesNotExist:
                logger.warning("Pet %s not found", pet_id)

        sale.save()
        return sale

    @staticmethod
    @transaction.atomic
    def process_payment(
        sale: Sale,
        method: str,
        amount: Decimal,
        reference: str = '',
        cash_drawer: Optional[CashDrawer] = None
    ) -> Payment:
        """
        Process a payment for the sale.
        
        Args:
            sale: The sale being paid.
            method: Payment method code.
            amount: Payment amount.
            reference: Payment reference number.
            cash_drawer: Optional cash drawer for cash payments.
            
        Returns:
            Created Payment instance.
            
        Raises:
            POSServiceError: If sale is not pending.
        """
        if sale.status != Sale.Status.PENDING:
            raise POSServiceError("Cannot process payment for non-pending sale")

        # Link cash drawer if not set
        if not sale.cash_drawer and cash_drawer:
            sale.cash_drawer = cash_drawer
            sale.save(update_fields=['cash_drawer'])

        # Create payment record
        payment = Payment.objects.create(
            sale=sale,
            method=method,
            amount=amount,
            reference=reference
        )

        # Update sale payment totals
        sale.amount_paid = sum(p.amount for p in sale.payments.all())
        sale.change_due = max(Decimal('0.00'), sale.amount_paid - sale.total)
        sale.save(update_fields=['amount_paid', 'change_due'])

        # Complete sale if fully paid
        if sale.is_fully_paid:
            sale.complete_sale()
            logger.info("Sale %s completed with payment %s", 
                       sale.transaction_id, payment.pk)

        return payment


class CashDrawerService:
    """Service class for cash drawer operations."""

    @staticmethod
    def get_open_drawer(branch: Branch) -> Optional[CashDrawer]:
        """Get the currently open drawer for a branch."""
        return CashDrawer.objects.filter(
            branch=branch,
            status=CashDrawer.Status.OPEN
        ).first()

    @staticmethod
    def open_drawer(
        branch: Branch,
        user: User,
        opening_amount: Decimal
    ) -> CashDrawer:
        """
        Open a new cash drawer.
        
        Args:
            branch: The branch.
            user: The user opening the drawer.
            opening_amount: Starting cash amount.
            
        Returns:
            New CashDrawer instance.
            
        Raises:
            POSServiceError: If drawer already open.
        """
        existing = CashDrawerService.get_open_drawer(branch)
        if existing:
            raise POSServiceError("A drawer is already open for this branch")

        drawer = CashDrawer.objects.create(
            branch=branch,
            opened_by=user,
            opening_amount=opening_amount,
            expected_cash=opening_amount
        )
        
        logger.info("Opened cash drawer %s for branch %s", drawer.pk, branch.pk)
        return drawer

    @staticmethod
    def close_drawer(
        drawer: CashDrawer,
        user: User,
        actual_cash: Decimal,
        notes: str = ''
    ) -> CashDrawer:
        """
        Close a cash drawer.
        
        Args:
            drawer: The drawer to close.
            user: The user closing.
            actual_cash: Actual cash counted.
            notes: Closing notes.
            
        Returns:
            Updated CashDrawer instance.
        """
        drawer.close_drawer(user, actual_cash, notes)
        logger.info(
            "Closed cash drawer %s. Variance: %s",
            drawer.pk, drawer.variance
        )
        return drawer


class InventoryService:
    """Service for POS inventory queries."""

    @staticmethod
    def get_available_services(branch: Branch) -> List[Service]:
        """Get services available at a branch."""
        return Service.objects.filter(
            Q(branch=branch) | Q(branch__isnull=True),
            active=True
        ).order_by('category', 'name')

    @staticmethod
    def get_available_products(
        branch: Branch,
        item_type: Optional[str] = None
    ) -> List[Product]:
        """
        Get products available at a branch.
        
        Args:
            branch: The branch.
            item_type: Optional filter for 'Product' or 'Medication'.
            
        Returns:
            QuerySet of available products.
        """
        qs = Product.objects.filter(
            branch=branch,
            is_available=True,
            stock_quantity__gt=0
        )
        
        if item_type:
            qs = qs.filter(item_type=item_type)
            
        return qs.order_by('category', 'name')

    @staticmethod
    def check_stock_availability(
        product_id: int,
        quantity: int,
        current_in_cart: int = 0
    ) -> Tuple[bool, int]:
        """
        Check if sufficient stock is available.
        
        Args:
            product_id: The product to check.
            quantity: Requested quantity.
            current_in_cart: Quantity already in cart.
            
        Returns:
            Tuple of (is_available, available_quantity).
        """
        try:
            product = Product.objects.get(pk=product_id)
            available = product.stock_quantity - current_in_cart
            return quantity <= available, available
        except Product.DoesNotExist:
            return False, 0
