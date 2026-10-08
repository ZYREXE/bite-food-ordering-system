from django.db import models
from django.contrib.auth.models import User

class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='foods/')

    def __str__(self):
        return self.name


# CART MODEL
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


# CART ITEM MODEL
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE
    )

    food = models.ForeignKey(
        FoodItem,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.food.name

# ORDER MODEL
class Order(models.Model):

    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('processing', 'Processing'),
        ('delivered',  'Delivered'),
        ('cancelled',  'Cancelled'),
    ]

    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at   = models.DateTimeField(auto_now_add=True)
    subtotal     = models.DecimalField(max_digits=8, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=40)
    total        = models.DecimalField(max_digits=8, decimal_places=2)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order #{self.id} — {self.user.username}"

    class Meta:
        ordering = ['-created_at']


# ORDER ITEM MODEL
class OrderItem(models.Model):

    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food     = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price    = models.DecimalField(max_digits=6, decimal_places=2)   # price snapshot

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.food.name} ×{self.quantity}"