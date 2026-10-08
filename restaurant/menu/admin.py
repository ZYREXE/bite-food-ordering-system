from django.contrib import admin
from .models import FoodItem, Cart, CartItem, Order, OrderItem

admin.site.register(FoodItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('food', 'quantity', 'price')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username',)
    inlines = [OrderItemInline]
    readonly_fields = ('user', 'subtotal', 'delivery_fee', 'total', 'created_at')

admin.site.register(Order, OrderAdmin)