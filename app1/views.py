
from django.shortcuts import render
from django.db.models import Q
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from app1.models import *
from django.conf import settings
from app_seller.models import *
from django.core.mail import send_mail
import random
from django.contrib.auth.hashers import make_password, check_password
# Create your views here.;


def index(request):
    try:
        request.session['email']
        session_user_data = User.objects.get(request.session['email'])
    except:
        return render(request, "index.html")
    
    
def search(request):
    if request.method == "POST":
        query = request.POST['ser']
        product_data = Product.objects.filter(
        Q(pname__icontains=query) | Q(desc__icontains=query))
        session_user_data = User.objects.get(username=request.session['email'])
        return render(request, "view_products.html", {"product_data": product_data, "session_user_data": session_user_data})
    
    
def forgot_password(request):
    if request.method == "POST":
        try:
            user_data = User.objects.get(username=request.POST['email'])
            request.session['f_email'] = request.POST['email']
            global votp
            votp = random.randint(100000, 999999)
            subject = 'EVIB ECOMMERECE OTP VERIFICATION MAIL'
            message = f'Your OTP IS {votp}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [request.POST['email'], ]
            send_mail(subject, message, email_from, recipient_list)
            return render(request, "f_otp.html")
        except:
            return render(request, "forgot_password.html", {"msg": "User Not Exist"})
    else:
        return render(request, "forgot_password.html")


def fotp(request):

    if request.method == "POST":
        # print(type(votp), type(request.POST['otp']))
        if votp == int(request.POST['otp']):
            return render(request, "reset_password.html")
        else:
            return render(request, "f_otp.html", {'msg': "OTP INCORRECT"})
    else:
        return render(request, "f_otp.html")



def reset_password(request):
    if request.method == "POST":
        if request.POST['pass'] == request.POST['cpass']:
            user_data = User.objects.get(username=request.session['f_email'])
            user_data.password = make_password(request.POST['pass'])
            user_data.save()
            del request.session['f_email']
            return render(request, "reset_password.html", {'msg': "PAsswrod Reset Succesfully", })
        else:
            return render(request, "reset_password.html", {'msg': "PAsswrod And confrim password not match"})
    else:
        return render(request, "reset_password.html")




def register(request):
    if request.method == "POST":
        try:
            User.objects.get(username=request.POST['email'])
            return render(request, "register.html", {'msg': "User Already Exist"})
        except:
            if request.POST['password'] == request.POST['cpassword']:
                global votp
                votp = random.randint(123456, 777483)
                subject = 'OTP VERIFICATION EVIB WEBSITE'
                message = f'YOUR OTP IS {votp}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [request.POST['email'], ]
                send_mail(subject, message, email_from, recipient_list)
                global temp
                temp = {
                    'fname': request.POST['fname'],
                    'uname': request.POST['email'],
                    'pass': make_password(request.POST['password'])
                }
                return render(request, "otp.html")
            else:
                return render(request, "register.html", {'msg': "Password and Confirm Password Not match"})
    else:
        return render(request, "register.html")


def otp(request):
    if request.method == "POST":
        if votp == int(request.POST['otp']):
            User.objects.create(
                fullname=temp['fname'],
                username=temp['uname'],
                password=temp['pass']
            )
            return render(request, "login.html", {'msg': "Registration SUccessful"})
        else:
            return render(request, "otp.html", {'msg': 'Invalid OTP'})
    else:
        return render(request, "otp.html")


def login(request):

    if request.method == "POST":
        try:
            user_data = User.objects.get(username=request.POST['email'])
            if check_password(request.POST["pass"], user_data.password):
                request.session['email'] = request.POST['email']
                request.session['name'] = user_data.fullname
                session_user_data = User.objects.get(
                    username=request.session['email'])
                return render(request, "index.html", {"session_user_data": session_user_data})
            else:
                return render(request, "login.html", {"msg": "Invalid Password"})
        except:
            return render(request, "login.html", {"msg": "Account Not exist please register"})
    else:
        return render(request, "login.html")


def profile(request):
    try:
        request.session['email']
        session_user_data = User.objects.get(username=request.session['email'])
        if request.method == "POST":
            user_data = User.objects.get(username=request.session['email'])
            if request.POST['pass']:
                if check_password(request.POST["opass"], user_data.password):
                    if request.POST['pass'] == request.POST['cpass']:
                        user_data = User.objects.get(
                            email=request.session['email'])
                        user_data.fullname = request.POST['fname']
                        user_data.password = make_password(
                            request.POST['pass'])
                        try:
                            request.FILES['propic']
                            user_data.profilepic = request.FILES['propic']
                            user_data.save()
                        except:
                            user_data.save()
                        return render(request, "profile.html", {"user_data": user_data, "msg": "Profile Updated Succesfully", "session_user_data": session_user_data})
                    else:
                        user_data = User.objects.get(
                            email=request.session['email'])
                        return render(request, "profile.html", {"user_data": user_data, "msg": "Password and Confirm Password Not Match", "session_user_data": session_user_data})
                else:
                    return render(request, "profile.html", {"user_data": user_data, "msg": "OLD PASSWORD NOT MATCH", "session_user_data": session_user_data})
            else:
                user_data = User.objects.get(username=request.session['email'])
                user_data.fullname = request.POST['fname']
                try:
                    request.FILES['propic']
                    user_data.profilepic = request.FILES['propic']
                    user_data.save()
                except:
                    user_data.save()
                return render(request, "profile.html", {"user_data": user_data, "msg": "Profile Updated Succesfully", "session_user_data": session_user_data})
        else:
            user_data = User.objects.get(username=request.session['email'])
            return render(request, "profile.html", {"user_data": user_data, "session_user_data": session_user_data})
    except:
        return render(request, "index.html")


def logout(request):
    try:
        request.session['email']
        del request.session['email']
        return render(request, 'index.html')
    except:
        return render(request, 'index.html')


def view_products(request):
    request.session['email']
    session_user_data = User.objects.get(username=request.session['email'])
    product_data = Product.objects.all()
    return render(request, "view_products.html", {"product_data": product_data, "session_user_data": session_user_data})


def product_description(request, pk):
    session_user_data = User.objects.get(username=request.session['email'])
    single_product = Product.objects.get(id=pk)
    return render(request, "product_description.html", {
        'single_product': single_product, "session_user_data": session_user_data})


def add_to_cart(request, pk):
    session_user_data = User.objects.get(username=request.session['email'])
    if request.method == "POST":
        usr = User.objects.get(username=request.session['email'])
        try:
            cart_exist = Cart.objects.get(product=pk, user=usr)
            cart_exist.quantity = cart_exist.quantity+1
            cart_exist.total = int(cart_exist.quantity) * \
                int(cart_exist.product.price)
            cart_exist.save()
        except:
            prod = Product.objects.get(id=pk)
            Cart.objects.create(
                product=prod,
                user=usr,
                quantity=1,
                total=prod.price
            )
        single_product = Product.objects.get(id=pk)
        return render(request, "product_description.html", {
            'single_product': single_product, "msg": "Cart Added Succesfully", "session_user_data": session_user_data})
         
def view_cart(request):
    try:
        user_data = User.objects.get(username=request.session['email'])
        total_cart = Cart.objects.filter(user=user_data)
        final_total = 0
        for i in total_cart:
            final_total += i.total
        return render(request, "cart.html", {"total_cart": total_cart, "final_total": final_total})
    except:
        return render(request, "index.html")
    
    
# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
	auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


def homepage(request):
	currency = 'INR'
	amount = 20000  # Rs. 200

	# Create a Razorpay Order
	razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                    currency=currency,
                                                    payment_capture='0'))

	# order id of newly created order.
	razorpay_order_id = razorpay_order['id']
	callback_url = 'paymenthandler/'

	# we need to pass these details to frontend.
	context = {}
	context['razorpay_order_id'] = razorpay_order_id
	context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
	context['razorpay_amount'] = amount
	context['currency'] = currency
	context['callback_url'] = callback_url

	return render(request, 'index.html', context=context)


# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
@csrf_exempt
def paymenthandler(request):

	# only accept POST request.
	if request.method == "POST":
		try:

			# get the required parameters from post request.
			payment_id = request.POST.get('razorpay_payment_id', '')
			razorpay_order_id = request.POST.get('razorpay_order_id', '')
			signature = request.POST.get('razorpay_signature', '')
			params_dict = {
				'razorpay_order_id': razorpay_order_id,
				'razorpay_payment_id': payment_id,
				'razorpay_signature': signature
			}

			# verify the payment signature.
			result = razorpay_client.utility.verify_payment_signature(
				params_dict)
			if result is not None:
				amount = 20000  # Rs. 200
				try:

					# capture the payemt
					razorpay_client.payment.capture(payment_id, amount)

					# render success page on successful caputre of payment
					return render(request, 'paymentsuccess.html')
				except:

					# if there is an error while capturing payment.
					return render(request, 'paymentfail.html')
			else:

				# if signature verification fails.
				return render(request, 'paymentfail.html')
		except:

			# if we don't find the required parameters in POST data
			return HttpResponseBadRequest()
	else:
        	# if other than POST request is made.
		return HttpResponseBadRequest()
