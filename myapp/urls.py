from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [

    path('login_get/',views.login_get),
    path('hotel_register/',views.hotel_register),
    path('hotel_register_post/',views.hotel_register_post),
    path('admin_home/',views.admin_home),
    path('verify_hotel/',views.verify_hotel),
    path('admin_change_password/',views.admin_change_password),
    path('view_user_details/',views.view_user_details),
    path('view_complaint/',views.view_complaint),
    path('send_reply/<id>/',views.send_reply),
    path('accept_hotel/<id>/',views.accept_hotel),
    path('reject_hotel/<id>/',views.reject_hotel),
    

    path('hotel_home/',views.hotel_home),
    path('updates_profile/',views.updates_profile),
    path('manage_food_items/',views.manage_food_items),
    path('add_leftover_food/',views.add_leftover_food),
    path('add_new/',views.add_new),
    path('edit_food_item/<id>/',views.edit_food_item),
    path('delete_food_item/<id>/',views.delete_food_item),
    path('manage_leftover_food/',views.manage_leftover_food),
    path('view_food_order_verify/',views.view_food_order_verify),
    path('view_leftover_food_order_verify/',views.view_leftover_food_order_verify),
    path('accept_order/<id>/',views.accept_order),
    path('reject_order/<id>/',views.reject_order),
    path('accept_leftover_order/<id>/',views.accept_leftover_order),
    path('reject_leftover_order/<id>/',views.reject_leftover_order),

    
    path('user_home/',views.user_home),
    path('user_register/',views.user_register),
    path('user_register_post/',views.user_register_post),
    path('update_profile/',views.update_profile),
    path('order_normal_food/<id>/',views.order_normal_food),
    path('order_leftover_food/<id>/',views.order_leftover_food),
    path('change_password/',views.change_password),
    path('user_view_food_items/',views.user_view_food_items),
    path('view_order_status/',views.view_order_status),
    path('view_leftover_food_request/',views.view_leftover_food_request),
    path('view_leftover_order_status/',views.view_leftover_order_status),
    path('send_complaint/',views.send_complaint),
    path('view_reply/',views.view_reply),
   

    


    

    
]
