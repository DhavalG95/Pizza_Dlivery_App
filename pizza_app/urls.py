from django.urls import path,include
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views


urlpatterns = [
   path('',home,name="home"),
   path('login_page',login_page,name="login_page"),
   path('register_page',register_page,name="register_page"),
   path('add_cart/<pizza_uid>',add_cart,name="add_cart"),
   path('cart',cart,name="cart"),
   path('remove_cart_items/<cart_item_uid>',remove_cart_items,name='remove_cart_items'),
   path('orders',orders,name='orders'),
   path('success',success,name='success'),
   path('logout', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns() 