from django.contrib import admin
from django.urls import path
from menu.views import CheckoutBillView, OrderSuccessView, Userregisterview,Checkoutview, Loginview, Logoutview, Homeview, ChangePasswordView,ChangeUsernameView,MenuView,AboutView,ProfileView,AddToCartView,CartView,IncreaseQuantityView,DecreaseQuantityView,RemoveCartItemView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/',admin.site.urls),
    path('register/',Userregisterview.as_view(), name='register'),
    path('login/',Loginview.as_view(),name='signin'),
    path('logout/',Logoutview.as_view(),name='logout'),
    path('',Homeview.as_view(),name='home'),
    path("change-password/",ChangePasswordView.as_view(), name="change_password"),
    path("change-username/",ChangeUsernameView.as_view(), name="change_username"),
    path('menu/',MenuView.as_view(),name='menu'),
    path('about/',AboutView.as_view(),name='about'),
    path('profile/',ProfileView.as_view(),name='profile'),
    path('add-to-cart/<int:id>/',AddToCartView.as_view(),name='add_to_cart'),
    path('cart/',CartView.as_view(),name='cart'),
    path('increase-quantity/<int:id>/',IncreaseQuantityView.as_view(),name='increase_quantity'),
    path('decrease-quantity/<int:id>/',DecreaseQuantityView.as_view(),name='decrease_quantity'),
    path('remove-cart-item/<int:id>/',RemoveCartItemView.as_view(),name='remove_cart_item'),
    path('payment/',Checkoutview.as_view(),name='checkout'),
    path('checkout/',CheckoutBillView.as_view(), name='checkout_bill'),
    path('order/<int:order_id>/success/', OrderSuccessView.as_view(), name='order_success'),
          
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)