from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from instamojo_wrapper import Instamojo
from django.conf import settings
from django.contrib.auth.decorators import login_required

api = Instamojo(api_key=settings.API_KEY,
                auth_token=settings.AUTH_TOKEN,
                endpoint='https://test.instamojo.com/api/1.1/')


# Create your views here.
def home(request):
    pizzas = Pizza.objects.all().values()
    return render(request,"home.html",context={"piz":pizzas})

def login_page(request):
    if request.method == "POST":
        try:
            username = request.POST.get('name')
            password = request.POST.get('pass')

            user_obj = User.objects.filter(username=username)
            if not user_obj.exists():
                messages.warn(request,'user not found...')
                return redirect('/register_page')
                
            if user_obj := authenticate(username=username,password=password):
                login(request,user_obj)
                return redirect('/')
            

            messages.error(request,'Wrong Password ...')
            return redirect('/login_page')

        except Exception as e:
            messages.error(request,"something went wrong..")
            return redirect('/register_page')

    return render(request,'login.html')

def register_page(request):
    if request.method == "POST":
        try:
            username = request.POST.get('name')
            password = request.POST.get('pass')

            user_obj = User.objects.filter(username=username)
            if user_obj.exists():
                messages.error(request,'username is taken...')
                return redirect('/register_page')
            else:
                user_obj= User.objects.create(username=username)
                user_obj.set_password(password)
                user_obj.save()

                messages.success(request,'Account Created...')
                return redirect('/login_page')

        except Exception as e:
            messages.error(request,"something went wrong..")
            return redirect('/register_page')

    return render(request,'register.html')


@login_required(login_url="/login_page")
def add_cart(request,pizza_uid):
    user = request.user
    pizza_obj =Pizza.objects.get(uid= pizza_uid)
    cart , _ = Cart.objects.get_or_create(user=user,is_paid=False)
    cart_items = CartItems.objects.create(cart=cart,pizza = pizza_obj)
    return redirect('/')


@login_required(login_url="/login_page")
def cart(request):
    cart_info = Cart.objects.get(is_paid=False,user=request.user)
    response = api.payment_request_create(
        amount = cart_info.get_cart_total(),
        purpose = "order",
        buyer_name = request.user.username,
        email = "dhavalgothir@gmail.com",
        redirect_url = "/success"

    )
    cart_info.instamojo_id = response['payment_request']['id']
    cart_info.save()
    return render(request,'cart.html',context={"carts":cart_info,"payment_url":response['payment_request']['longurl']})


@login_required(login_url="/login_page")
def remove_cart_items(request,cart_item_uid):
    try:

        CartItems.objects.get(uid=cart_item_uid).delete()
        return redirect('cart')

    except Exception as e:
        print(e)


@login_required(login_url="/login_page")
def orders(request):
    orders = Cart.objects.filter(is_paid=True,user=request.user)
    return render(request,'orders.html',context={"orders":orders})


@login_required(login_url="/login_page")
def success(request):
    payment_request = request.GET.get('payment_request_id')
    cartinfo = Cart.objects.get(instamojo_id = payment_request)
    cartinfo.is_paid = True
    cartinfo.save()
    return redirect('orders')
