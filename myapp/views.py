from django.shortcuts import redirect, render
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User,Group
from django.contrib.auth import authenticate
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import login
from django.db import models
from django.template.context_processors import request
from myapp.models import *
from datetime import datetime
from django.contrib.auth.hashers import check_password
from django.contrib.auth import logout
from django.forms import EmailField
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from .models import user_table, hotel_table, complaint_table

# Create your views here.
def login_get(request):
    if request.method =='POST':
        username=request.POST['username']
        password=request.POST['password']
        guest=authenticate(username=username,password=password)
        if guest is not None:
            if guest.groups.filter(name='admin').exists():
                login(request,guest)
                return redirect('/myapp/admin_home')
            elif guest.groups.filter(name='user').exists():
                login(request,guest)
                return redirect('/myapp/user_home')
            elif guest.groups.filter(name='hotel').exists():
                ob=hotel_table.objects.get(LOGIN=guest)
                if ob.status=='Approved':
                    login(request,guest)
                    return redirect('/myapp/hotel_home')
                else:
                    messages.error(request,'Wait for verification!!')
                    return redirect('/myapp/login_get/')
            else:
                messages.error(request,'Invalid Username Or Password')
                return redirect('/myapp/login_get/')
        else:
            messages.error(request,'Invalid Username Or Password')
            return redirect('/myapp/login_get/')

    return render(request,'login.html')




def hotel_register(request):
    return render(request,'hotel_register.html')

def hotel_register_post(request):
    username=request.POST['username']
    password=request.POST['password']
    name=request.POST['name']
    email=request.POST['email']
    phone=request.POST['phone']
    logo=request.FILES['logo']
    proof=request.FILES['proof']
    address=request.POST['address']

    if User.objects.filter(username=username).exists():
        messages.error(request,'Username already Taken')
        return redirect('/myapp/login_get/')
    user=User.objects.create_user(username=username,password=password)
    user.save()
    user.groups.add(Group.objects.get(name='hotel'))


    ob=hotel_table()
    ob.name=name
    ob.email=email
    ob.phone=phone
    ob.logo=logo
    ob.proof=proof
    ob.address=address
    ob.LOGIN=user
    ob.save()
    messages.success(request,'Registration successful Wait for verification!!')
    return redirect('/myapp/login_get/')

def user_register(request):
    return render(request,'user_register.html')

def user_register_post(request):
    username=request.POST['username']
    password=request.POST['password']
    name=request.POST['name']
    email=request.POST['email']
    phone=request.POST['phone']
    photo=request.FILES['photo']
    address=request.POST['address']
    ob=user_table()
    ob.name=name
    ob.email=email
    ob.phone=phone
    ob.photo=photo
    ob.address=address
    if User.objects.filter(username=username).exists():
        messages.error(request,'Username already Taken')
        return redirect('/myapp/login_get/')
    user=User.objects.create_user(username=username,password=password)
    user.save()
    user.groups.add(Group.objects.get(name='user'))
    ob.LOGIN=user
    ob.save()
    messages.success(request,'Registration successful!!')
    return redirect('/myapp/login_get')


   









def admin_home(request):
    
    active_users = user_table.objects.count()

    total_hotels = hotel_table.objects.count()
    pending_hotels = hotel_table.objects.filter(status='pending').count()
    approved_hotels = hotel_table.objects.filter(status='Approved').count()

    total_complaints = complaint_table.objects.count()
    open_complaints = complaint_table.objects.filter(replay='pending').count()
    resolved_complaints = total_complaints - open_complaints

    hotel_rate = int((approved_hotels / total_hotels * 100)) if total_hotels > 0 else 0
    complaint_rate = int((resolved_complaints / total_complaints * 100)) if total_complaints > 0 else 0

    context = {
        'active_users': active_users,
        'total_hotels': total_hotels,
        'pending_hotels': pending_hotels,
        'approved_hotels': approved_hotels,
        'total_complaints': total_complaints,
        'open_complaints': open_complaints,
        'resolved_complaints': resolved_complaints,
        'hotel_rate': hotel_rate,
        'complaint_rate': complaint_rate,
    }
    
    return render(request, 'admin/admin_home.html', context)

def verify_hotel(request):
    ob=hotel_table.objects.all()
    return render(request,'admin/verify_hotel.html',{'data':ob})

def accept_hotel(request ,id):
    ob=hotel_table.objects.get(id=id)
    ob.status='Approved'
    ob.save()
    return redirect('/myapp/verify_hotel/')
    
def reject_hotel(request, id):
    ob=hotel_table.objects.get(id=id)
    ob.status='Rejected'
    ob.save()
    return redirect('/myapp/verify_hotel/')

def admin_change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        if new_password == confirm_password:
            f = check_password(current_password, request.user.password)
            if f:
                user = request.user
                user.set_password(new_password)
                user.save()
                logout(request)
                messages.success(request, 'password updated successfully.')
                return redirect('/myapp/login_get/')
            else:
                messages.warning(request, 'Invalid Current Password.')
                return redirect('/myapp/admin_change_password/')
        else:
            messages.warning(request, 'new password and confirm password are not equal')
            return redirect('/myapp/admin_change_password/')
    else:
        return render(request,'admin/change_password.html')

def view_user_details(request):
    ob=user_table.objects.all()
    return render(request,'admin/view_user.html',{'data':ob})

def view_complaint(request):
    ob=complaint_table.objects.all()
    return render(request,'admin/view_complaint.html',{'data':ob})

def send_reply(request,id):
    ob=complaint_table.objects.get(id=id)
    if request.method == 'POST':
        replay=request.POST['replay']
        ob.replay=replay
        ob.save()
        return redirect('/myapp/view_complaint/')
    return render(request,'admin/send_reply.html',{'data':ob})











@login_required(login_url='/myapp/login_get/')
def hotel_home(request):
    try:
        hotel = hotel_table.objects.get(LOGIN=request.user)
    except hotel_table.DoesNotExist:
        hotel = None

    if hotel:
        active_deals = leftover_foodtable.objects.filter(FOOD__HOTEL=hotel, status='Active').count()

        pending_standard = order_table.objects.filter(FOOD__HOTEL=hotel, status='ordered').count()

        pending_leftover = leftover_order_table.objects.filter(LEFT__FOOD__HOTEL=hotel, status='ordered').count()
    else:
        active_deals = pending_standard = pending_leftover = 0

    context = {
        'hotel': hotel,
        'active_deals': active_deals,
        'pending_standard': pending_standard,
        'pending_leftover': pending_leftover,
    }
    
    return render(request, 'hotel/hotel_home.html', context)

def updates_profile(request):
    ob=hotel_table.objects.get(LOGIN=request.user)
    if request.method=='POST':
        name=request.POST['name']
        email=request.POST['email']
        phone=request.POST['phone']
        address=request.POST['address']
        ob.name=name
        ob.email=email
        ob.phone=phone
        if 'logo' in request.FILES:
            logo=request.FILES['logo']
            ob.logo=logo
        ob.address=address
        ob.save()
        return redirect('/myapp/updates_profile/')
    return render(request,'hotel/updates_profile.html',{'data':ob})

def manage_food_items(request):
    ob=food_table.objects.filter(HOTEL__LOGIN=request.user,status='Active')
    return render(request,'hotel/manage_food_items.html',{'data':ob})

def add_new(request):
    if request.method=='POST':
        name=request.POST['name']
        details=request.POST['details']
        image=request.FILES['image']
        quantity=request.POST['quantity']
        price=request.POST['price']
        ob=food_table()
        ob.name=name
        ob.details=details
        ob.image=image
        ob.mfg=datetime.today()
        ob.price=price
        ob.quantity=quantity
        ob.status='Active'
        ob.HOTEL=hotel_table.objects.get(LOGIN=request.user)
        ob.save()
        return redirect('/myapp/manage_food_items/')
    return render(request,'hotel/add_new.html')

def edit_food_item(request, id):
    ob=food_table.objects.get(id=id)
    if request.method=='POST':
        name=request.POST['name']
        details=request.POST['details']
        quantity=request.POST['quantity']
        price=request.POST['price']
        
        ob.name=name
        ob.details=details
        if 'image' in request.FILES:
            image=request.FILES['image']
            ob.image=image
        ob.mfg=datetime.today()
        ob.price=price
        ob.quantity=quantity
        ob.HOTEL=hotel_table.objects.get(LOGIN=request.user)
        ob.save()
        return redirect('/myapp/manage_food_items/')
    return render(request,'hotel/edit_food_item.html',{'data':ob})

def delete_food_item(request, id):
    food_table.objects.get(id=id).delete()
    return redirect('/myapp/manage_food_items/')

def manage_leftover_food(request):
    ob=leftover_foodtable.objects.filter(FOOD__HOTEL__LOGIN=request.user)
    return render(request,'hotel/manage_leftover_food.html',{'data':ob})




def add_leftover_food(request):
    ob=food_table.objects.filter(HOTEL__LOGIN=request.user,status='Active')
    if request.method == 'POST':
        food=request.POST['food']
        discountprice=request.POST['discount_price']
        valid=request=request.POST['valid']
        ob=leftover_foodtable()
        ob.FOOD=food_table.objects.get(id=food)
        ob.discountprice=discountprice
        ob.valid=valid
        ob.status='Active'
        ob.save()
        ob1=food_table.objects.get(id=food)
        ob1.status='Inactive'
        ob1.save()
        return redirect('/myapp/manage_leftover_food/')

    return render(request,'hotel/add_discount_price.html',{'data':ob})


def view_food_order_verify(request):
    ob=order_table.objects.filter(FOOD__HOTEL__LOGIN=request.user)
    return render(request,'hotel/view_food_order_verify.html',{'data':ob})


def accept_order(request, id):
    ob=order_table.objects.get(id=id)
    if ob.status != 'Accepted':
        food=ob.FOOD
        food.quantity=max(food.quantity - ob.quantity, 0)
        if food.quantity <= 0:
            food.status='Inactive'
        food.save()
        ob.status='confirmed'
        ob.save()
    return redirect('/myapp/view_food_order_verify/')
    
def reject_order(request, id):
    ob=order_table.objects.get(id=id)
    ob.status='Rejected'
    ob.save()
    return redirect('/myapp/view_food_order_verify/')

def view_leftover_food_order_verify(request):
    ob=leftover_order_table.objects.filter(LEFT__FOOD__HOTEL__LOGIN=request.user)
    return render(request,'hotel/view_leftover_food_order_verify.html',{'data':ob})

def accept_leftover_order(request, id):
    ob=leftover_order_table.objects.get(id=id)
    if ob.status != 'Accepted':
        food=ob.LEFT.FOOD
        food.quantity=max(food.quantity - ob.quantity, 0)
        if food.quantity <= 0:
            food.status='Inactive'
        food.save()
        ob.status='confirmed'
        ob.save()
    return redirect('/myapp/view_leftover_food_order_verify/')

def reject_leftover_order(request, id):
    ob=leftover_order_table.objects.get(id=id)
    ob.status='Rejected'
    ob.save()
    return redirect('/myapp/view_leftover_food_order_verify/')












def user_home(request):
    leftover = leftover_foodtable.objects.filter(status='Active').order_by('-id')[:20]
    normal = food_table.objects.filter(status='Active').order_by('-id')[:20]
    user = user_table.objects.get(LOGIN=request.user)
    return render(request, 'user/user_home.html', {
        'leftover': leftover,
        'normal': normal,
        'user': user
    })

def update_profile(request):
    ob=user_table.objects.get(LOGIN=request.user)
    if request.method=='POST':
        name=request.POST['name']
        email=request.POST['email']
        phone=request.POST['phone']
        address=request.POST['address']
        ob.name=name
        ob.email=email
        ob.phone=phone
        ob.address=address
        if 'photo' in request.FILES:
            photo=request.FILES['photo']
            ob.photo=photo
        ob.save()
        return redirect('/myapp/update_profile/')
    return render(request,'user/update_profile.html',{'data':ob})


def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        if new_password == confirm_password:
            f = check_password(current_password, request.user.password)
            if f:
                user = request.user
                user.set_password(new_password)
                user.save()
                logout(request)
                messages.success(request, 'password updated successfully.')
                return redirect('/myapp/login_get/')
            else:
                messages.warning(request, 'Invalid Current Password.')
                return redirect('/myapp/change_password/')
        else:
            messages.warning(request, 'new password and confirm password are not equal')
            return redirect('/myapp/change_password/')
    else:
        return render(request,'user/change_password.html')

def user_view_food_items(request):
    ob=food_table.objects.filter(status='Active')
    return render(request,'user/view_normal_menu.html',{'data':ob})

def order_normal_food(request,id):
    ob=food_table.objects.get(id=id)
    if request.method=='POST':
        quantity=request.POST['quantity']
        od=order_table()
        od.FOOD=food_table.objects.get(id=id)
        od.USER=user_table.objects.get(LOGIN=request.user)
        od.quantity=quantity
        od.date=datetime.today()
        od.status='ordered'
        od.save()
        return redirect('/myapp/view_order_status/')

    return render(request,'user/order_qty.html',{'data':ob})

def view_order_status(request):
    ob=order_table.objects.filter(USER__LOGIN=request.user)
    return render(request,'user/view_order_status.html',{'data':ob}) 

import razorpay
from django.shortcuts import render, redirect

def payment_page_normal(request, id):
    order_obj = order_table.objects.get(id=id)
    
    total_amount = order_obj.quantity * order_obj.FOOD.price
    
    razorpay_api_key = "rzp_test_MJOAVy77oMVaYv"
    razorpay_secret_key = "MvUZ03MPzLq3lkvMneYECQsk"
    razorpay_client = razorpay.Client(auth=(razorpay_api_key, razorpay_secret_key))

    amount_in_paise = int(total_amount * 100)

    order_data = {
        'amount': amount_in_paise,
        'currency': 'INR',
        'receipt': f'std_rcpt_{order_obj.id}',
        'payment_capture': '1',  
    }

    rzp_order = razorpay_client.order.create(data=order_data)

    context = {
        'razorpay_api_key': razorpay_api_key,
        'amount': order_data['amount'],
        'currency': order_data['currency'],
        'rzp_order_id': rzp_order['id'],
        'order': order_obj, 
        'total_display': total_amount
    }

    return render(request, 'user/payment_page_normal.html', context)


def payment_success_normal(request, id):
    order_obj = order_table.objects.get(id=id)
    order_obj.status = 'paid'  # Update standard order table
    order_obj.save()
    
    return redirect('/myapp/view_order_status/')

def view_leftover_food_request(request):
    ob=leftover_foodtable.objects.filter(status='Active')
    return render(request,'user/view_leftover_food_request.html',{'data':ob})

def order_leftover_food(request,id):
    od=leftover_foodtable.objects.get(id=id)
    if request.method=='POST':
        quantity=request.POST['quantity']
        ob=leftover_order_table()
        ob.quantity=quantity
        ob.USER=user_table.objects.get(LOGIN=request.user)
        ob.LEFT=leftover_foodtable.objects.get(id=id)
        ob.date=datetime.today()
        ob.status='ordered'
        ob.save()
        return redirect('/myapp/view_leftover_order_status/')
    return render(request,'user/view_more.html',{'data':od})



def view_leftover_order_status(request):
    ob=leftover_order_table.objects.filter(USER__LOGIN=request.user)
    return render(request,'user/view_leftover_order_status.html',{'data': ob})


def send_complaint(request):
    if request.method == 'POST':
        complaint=request.POST['complaint']
        ob=complaint_table()
        ob.USER=user_table.objects.get(LOGIN=request.user)
        ob.complaint=complaint
        ob.date=datetime.today()
        ob.replay='pending'
        ob.save()
        return redirect('/myapp/view_reply/')
    return render(request,'user/send_complaint.html')

def view_reply(request):
    us=User.objects.get(id=request.user.id)
    user=user_table.objects.get(LOGIN=us)
    ob=complaint_table.objects.filter(USER=user)
    return render(request,'user/view_replies.html',{'data':ob})

import razorpay
from django.shortcuts import render, redirect
from datetime import datetime

def payment_page(request, id):
    order_obj = leftover_order_table.objects.get(id=id)
    
    total_amount = order_obj.quantity * order_obj.LEFT.discountprice
    
    razorpay_api_key = "rzp_test_MJOAVy77oMVaYv"
    razorpay_secret_key = "MvUZ03MPzLq3lkvMneYECQsk"
    razorpay_client = razorpay.Client(auth=(razorpay_api_key, razorpay_secret_key))

    amount_in_paise = int(total_amount * 100)

    order_data = {
        'amount': amount_in_paise,
        'currency': 'INR',
        'receipt': f'lefto_rcpt_{id}',   
        'payment_capture': '1',  
    }

    rzp_order = razorpay_client.order.create(data=order_data)

    context = {
        'razorpay_api_key': razorpay_api_key,
        'amount': order_data['amount'],
        'currency': order_data['currency'],
        'rzp_order_id': rzp_order['id'],
        'order': order_obj, 
        'total_display': total_amount
    }

    return render(request, 'user/payment_page.html', context)


def payment_success(request, id):
    order_obj = leftover_order_table.objects.get(id=id)
    order_obj.status = 'paid'
    order_obj.save()
    
    return redirect('/myapp/view_leftover_order_status/')
                         

