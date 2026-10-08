from urllib import request
from django.shortcuts import render, redirect
from django.views.generic import View
from menu.forms import Userregistration, Loginform, UsernameChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .models import FoodItem, Cart, CartItem, Order, OrderItem

# REGISTER
class Userregisterview(View):

    def get(self, request):
        form = Userregistration()
        return render(request, "register.html", {"form": form})

    def post(self, request):
        form = Userregistration(request.POST)

        if form.is_valid():

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')

            User.objects.create_user(
                username=username,
                password=password,
                email=email
            )

            return redirect("signin")

        else:
            print(form.errors)

        return render(request, "register.html", {"form": form})

#  LOGIN 
class Loginview(View):
    def get(self, request):
        form = Loginform()
        return render(request, "login.html", {"form": form})
    def post(self, request):
        form = Loginform(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect("home")     
        return render(request, "login.html", {"form": form})


# LOGOUT 
class Logoutview(View):
    def get(self, request):
        logout(request)
        return redirect("signin")       


#  HOME (after login) 
class Homeview(View):
    def get(self, request):
        return render(request, "home.html")
    

# change Password 
class ChangePasswordView(View):

    def get(self, request):

        if not request.user.is_authenticated:
            return redirect("signin")

        form = PasswordChangeForm(user=request.user)

        return render(request, "change_password.html", {
            "form": form
        })


    def post(self, request):

        if not request.user.is_authenticated:
            return redirect("signin")

        form = PasswordChangeForm(
            user=request.user,
            data=request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Password updated successfully! Please login again."
            )

            logout(request)

            return redirect("signin")

        return render(request, "change_password.html", {
            "form": form
        })

# Change username 
from menu.forms import UsernameChangeForm

class ChangeUsernameView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("signin")

        form = UsernameChangeForm(instance=request.user)
        return render(request, "change_username.html", {"form": form})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("signin")

        form = UsernameChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("home")

        return render(request, "change_username.html", {"form": form})
    
     
#  Menu

class MenuView(View):
    def get(self, request):
        foods = FoodItem.objects.all()
        return render(request, "menu.html", {"foods": foods})
    

# About 
class AboutView(View):
    def get(self, request):
        return render(request, "about.html")
    

# profile
class ProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("signin")
        return render(request, "profile.html")
    
# cart view
class AddToCartView(View):

    def get(self, request, id):

        # CHECK LOGIN
        if not request.user.is_authenticated:
            return redirect("signin")

        # GET FOOD ITEM
        food = FoodItem.objects.get(id=id)

        # GET OR CREATE CART
        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        # CHECK IF FOOD ALREADY IN CART
        cart_item = CartItem.objects.filter(
            cart=cart,
            food=food
        ).first()

        # IF EXISTS INCREASE QUANTITY
        if cart_item:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(
            request,f"{food.name} quantity updated in cart!")

        else:
            CartItem.objects.create(
            cart=cart,
            food=food,
            quantity=1)
            messages.success(request,f"{food.name} added to cart!")
        return redirect("menu")
    

class CartView(View):

    def get(self, request):

        # LOGIN CHECK
        if not request.user.is_authenticated:
            return redirect("signin")

        # GET USER CART
        cart = Cart.objects.filter(
            user=request.user
        ).first()

        # EMPTY CART DEFAULT
        cart_items = []
        total = 0

        # IF CART EXISTS
        if cart:

            cart_items = CartItem.objects.filter(
                cart=cart
            )

            # CALCULATE TOTAL
            for item in cart_items:
                total += item.food.price * item.quantity

        return render(request, "cart.html", {
            "cart_items": cart_items,
            "total": total
        })
    
# Payment of total amount
class CheckoutBillView(View):

    def get(self, request):

        if not request.user.is_authenticated:
            return redirect("signin")

        cart = Cart.objects.filter(user=request.user).first()
        cart_items = []
        subtotal   = 0

        if cart:
            cart_items = CartItem.objects.filter(cart=cart).select_related('food')
            for item in cart_items:
                subtotal += item.food.price * item.quantity

        if not cart_items:
            return redirect("cart")

        delivery_fee = 40
        total = subtotal + delivery_fee

        return render(request, "checkout.html", {
            "cart_items":   cart_items,
            "subtotal":     subtotal,
            "delivery_fee": delivery_fee,
            "total":        total,
        })

    def post(self, request):

        if not request.user.is_authenticated:
            return redirect("signin")

        cart = Cart.objects.filter(user=request.user).first()

        if not cart:
            return redirect("cart")

        cart_items = CartItem.objects.filter(cart=cart).select_related('food')

        if not cart_items.exists():
            return redirect("cart")

        # --- calculate ---
        subtotal     = sum(i.food.price * i.quantity for i in cart_items)
        delivery_fee = 40
        total        = subtotal + delivery_fee

        # --- create order ---
        order = Order.objects.create(
            user         = request.user,
            subtotal     = subtotal,
            delivery_fee = delivery_fee,
            total        = total,
            status       = 'pending',
        )

        # --- snapshot each item ---
        for item in cart_items:
            OrderItem.objects.create(
                order    = order,
                food     = item.food,
                quantity = item.quantity,
                price    = item.food.price,
            )

        # --- clear cart ---
        cart_items.delete()

        messages.success(request, f"Order #{order.id} placed! We're on it. 🎉")
        return redirect("order_success", order_id=order.id)


# ORDER SUCCESS PAGE
class OrderSuccessView(View):

    def get(self, request, order_id):

        if not request.user.is_authenticated:
            return redirect("signin")

        order = Order.objects.prefetch_related('items__food').get(
            id=order_id, user=request.user
        )

        return render(request, "order_success.html", {"order": order})


# keep the old Checkoutview pointing to the bill page (or remove it)
class Checkoutview(View):
    def get(self, request):
        return redirect("checkout_bill")
    


# quantity increase view
class IncreaseQuantityView(View):

    def get(self, request, id):

        # LOGIN CHECK
        if not request.user.is_authenticated:
            return redirect("signin")

        # GET CART ITEM
        cart_item = CartItem.objects.get(id=id)

        # INCREASE QUANTITY
        cart_item.quantity += 1

        # SAVE
        cart_item.save()

        return redirect("cart")
# quantity decrease view
class DecreaseQuantityView(View):

    def get(self, request, id):

        # LOGIN CHECK
        if not request.user.is_authenticated:
            return redirect("signin")

        # GET CART ITEM
        cart_item = CartItem.objects.get(id=id)

        # IF QUANTITY > 1
        if cart_item.quantity > 1:

            cart_item.quantity -= 1
            cart_item.save()

        # IF QUANTITY == 1 DELETE ITEM
        else:
            cart_item.delete()

        return redirect("cart")
    
#  Remove from cart view
class RemoveCartItemView(View):

    def get(self, request, id):

        # LOGIN CHECK
        if not request.user.is_authenticated:
            return redirect("signin")

        # GET ITEM
        cart_item = CartItem.objects.get(id=id)

        # DELETE ITEM
        cart_item.delete()

        return redirect("cart")