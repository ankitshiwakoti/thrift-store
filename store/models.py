from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [
        ("AVAILABLE", "Available"),
        ("SOLD", "Sold"),
    ]

    CONDITION_CHOICES = [
        ("NEW", "New"),
        ("LIKE_NEW", "Like New"),
        ("GOOD", "Good"),
        ("FAIR", "Fair"),
    ]

    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    image = models.ImageField(upload_to="products/", null=True, blank=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_items(self):
        return self.items.count()

    @property
    def total_price(self):
        return sum(i.subtotal for i in self.items.select_related("product"))
    
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return self.product.name

    @property
    def subtotal(self):
        return self.product.price
    
    from django.conf import settings

class Order(models.Model):
    STATUS_CHOICES = [
        ("PLACED", "Placed"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    address = models.TextField()
    notes = models.TextField(blank=True)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PLACED")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # store price at time of order
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
