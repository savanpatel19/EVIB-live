from django.shortcuts import render
from app_seller.models import *
from django.conf import settings
from django.core.mail import send_mail
import random
from django.contrib.auth.hashers import make_password,check_password


# Create your views here.
def seller_index(request):
    return render(request,'seller_index.html')

def seller_register(request):
    if request.method =="POST":
        try:
            seller_user.objects.get(seller_username = request.POST['email'])
            return render(request,'seller_register.html',{"msg":"USER ALREADY EXISTS"})
        except:
            if request.POST['password']== request.POST['cpassword']:
                global seller_otp
                seller_otp=random.randint(123456,321456)
                subject = 'SELLER OTP VERIFICATION EVIB WEBSITE'
                message = f'YOUR OTP IS {seller_otp}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [request.POST['email'], ]
                send_mail( subject, message, email_from, recipient_list )
                global seller_temp
                seller_temp={
                    's_fname':request.POST['fname'],
                    's_uname':request.POST['email'],
                    's_pass' :make_password(request.POST['password'])
                }
                return render(request,'seller_otp.html')  
            else:
                return render(request,'seller_register.html',{"msg":"WRONG PASSWORD"})   
    else:
       return render(request,'seller_register.html')
   
   
def seller_otp(request):
    if request.method=='POST':
        if seller_otp==int(request.POST['otp']):
            seller_user.objects.create(
                seller_fullname=seller_temp['s_fname'],
                seller_username=seller_temp['s_uname'],
                seller_password=seller_temp['s_pass']
            )
            return render(request,'seller_login.html')
        else:
            return render(request,'seller_otp.html',{'msg':'INVALIDE OTP'})
    else:
        return render(request,'seller_otp.html')
    
def seller_login(request):
    if request.method=='POST':
        try:
          seller_user_data=seller_user.objects.get(seller_username=request.POST['email'])
          if check_password(request.POST['pass'],seller_user_data.seller_password):
              request.session['selleremail']=request.POST['email']
              request.session['sellername']=seller_user_data.seller_fullname
              return render(request,'seller_homepage.html')
          else:
              return render(request,'seller_login.html',{'msg':"PASSWORD INCORRECT"})
          
        except:
            return render(request,'seller_login.html',{'msg':'YOUR EMAIL IS NOT REGISTER'})
        
    else:
        return render(request,'seller_login.html')   
    
    
    
def seller_profile(request): 
    if request.method=='POST':
        seller_user_data = seller_user.objects.get(seller_username=request.session['selleremail'])
        if request.POST['pass']:
             if check_password(request.POST["opass"], seller_user_data.seller_password):
                if request.POST['pass'] == request.POST['cpass']:
                    seller_user_data = seller_user.objects.get(
                    seller_username=request.session['selleremail'])
                    seller_user_data.seller_fullname = request.POST['fname']
                    seller_user_data.seller_password = make_password(request.POST['pass'])
                    seller_user_data.save()
                    return render(request, "seller_profile.html", {"seller_user_data": seller_user_data, "msg": "Seller Profile Updated Succesfully"})
                else:
                    seller_user_data = seller_user.objects.get(
                    seller_username=request.session['selleremail'])
                    return render(request, "seller_profile.html", {"seller_user_data": seller_user_data, "msg": "Password and Confirm Password Not Match"})
             else:
                return render(request, "seller_profile.html", {"seller_user_data": seller_user_data, "msg": "OLD PASSWORD NOT MATCH"})
        else:
            seller_user_data=seller_user.objects.get(seller_username = request.session['selleremail'])
            seller_user_data.seller_fullname=request.POST['fname']
            seller_user_data.save()
            return render(request,"seller_profile.html",{'seller_user_data':seller_user_data,"msg":" SELLERS PROFILE UPDATED SUCCESSFULLY"})
            
    else:
        seller_user_data=seller_user.objects.get(seller_username=request.session['selleremail'])
        return render(request,'seller_profile.html',{'seller_user_data':seller_user_data})
    
    
    
def add_product(request):
    if request.method == "POST":
        seller_user_data = seller_user.objects.get( seller_username =request.session['selleremail'])
        try:
            request.FILES['ppic']
            Product.objects.create(
                pname=request.POST['pname'],
                price=request.POST['price'],
                pimage=request.FILES['ppic'],
                desc=request.POST['desc'],
                seller=seller_user_data
            )
        except:
            Product.objects.create(
                pname=request.POST['pname'],
                price=request.POST['price'],
                desc=request.POST['desc'],
                seller=seller_user_data
            )
        return render(request, "add_product.html", {"msg": "Product Added Succesfully"})
    else:
        return render(request, "add_product.html")
        
        
        
        
        
    
    