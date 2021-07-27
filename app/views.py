from django.shortcuts import render, redirect
from django.views import View
from .models import *
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail  
from django.conf import settings
import string
import random

from .utils import generate_checksum, verify_checksum,generate_refund_checksum
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ValidationError
from json import dumps
from urllib import request as rq, parse


from .models import PaytmDataBase 

paytm_sets = settings.PAYTM_GATEWAY_SETTINGS
txn_status_url = '/merchant-status/getTxnStatus'
txn_request_url = '/theia/processTransaction'

# prefer dash board for refunds
rfnd_request_url = '/refund/HANDLER_INTERNAL/REFUND'
rfnd_status_url = '/refund/HANDLER_INTERNAL/getRefundStatus'

class TestPaytm(TemplateView):
    template_name = 'app/checkout.html'


@method_decorator(csrf_exempt, name='dispatch')
class PaytmRequest(LoginRequiredMixin, TemplateView):
    template_name = 'app/request.html'

    def get_payment_data(self):
        req_data = {}

        if self.request.POST.get('PAYMENT_MODE_ONLY') == 'Yes':
            if not all(key in self.request.POST for key in ('AUTH_MODE', 'PAYMENT_TYPE_ID', 'CARD_TYPE', 'BANK_CODE')):
                raise ValidationError("please provide all these fields too: ('AUTH_MODE', 'PAYMENT_TYPE_ID', 'CARD_TYPE', 'BANK_CODE')")

        req_data.update(dict(map(lambda key:key, paytm_sets.items())))

        req_data.update(dict(map(lambda key:key, self.request.POST.items())))
        req_data.pop('csrfmiddlewaretoken', None)

        return req_data


    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['paytm_req_data'] = self.get_payment_data()

        ctx['paytm_req_data'].update({
                'CHECKSUMHASH':generate_checksum(ctx['paytm_req_data'], settings.PAYTM_MERCHANT_KEY)
            })

        ctx['paytm_url'] = settings.PAYTM_URL+txn_request_url
        return ctx

    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)



@method_decorator(csrf_exempt, name='dispatch')
class PaytmResponse(TemplateView):

    template_name = 'app/response.html'

    def save_transection(self, response_data):
        PaytmDataBase.objects.update_or_create(order_id=response_data.get('ORDERID'), 
                                amount=response_data.get('TXNAMOUNT'),
                                checksumhash=response_data.get('CHECKSUMHASH'),
                                txn_id=response_data.get('TXNID'),
                                status=response_data.get('STATUS'),
                                txndate=response_data.get('TXNDATE'),
                                banktxnid=response_data.get('BANKTXNID'),
                                
                               )
        
        
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        response_data = {}
        for key, value in self.request.POST.items():
            response_data.update({key:value})
        print(response_data.get('ORDERID'))

        if settings.PAYTM_SAVE_SUCCESS_TRANSECTIONS_ONLY:
            if response_data.get('RESPCODE') == '01':
                self.save_transection(response_data)
        else:
            self.save_transection(response_data)

        verified = verify_checksum(response_data, settings.PAYTM_MERCHANT_KEY, response_data['CHECKSUMHASH'])
        response_data.update({'checksum verified': verified })

        ctx['response_data'] = dumps(response_data)
        return ctx

    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@login_required
def paytm_transection_status(request):
    t=92271
    order=PaytmDataBase.objects.get(order_id=t)
    user=request.user
    context = {'order':order,'user':user}
    
    return render(request,'app/response.html',context)

  
def mail(request):  
    subject = "Greetings"  
    msg     = "Congratulations for your success"  
    to      = "erankitgate@@gmail.com"  
    res     = send_mail(subject, msg, settings.EMAIL_HOST_USER, [to])  
    if(res == 1):  
        msg = "Mail Sent Successfuly"  
    else:  
        msg = "Mail could not sent"  
    return HttpResponse(msg)  


# @method_decorator(login_required, name='dispatch')
class ProductView(View):
    def get(self, request):
        totalitem = 0
        laptop = Product.objects.filter(category='L')
        Mobile=Product.objects.filter(category='M')
        tablet=Product.objects.filter(category='T')
        PC=Product.objects.filter(category='PC')
        toys=Product.objects.filter(category='TO')
        BabyCare=Product.objects.filter(category='BC')
        SS=Product.objects.filter(category='SS')
        MW=Product.objects.filter(category='MW')
        WW=Product.objects.filter(category='WW')
        G=Product.objects.filter(category='G')
        W=Product.objects.filter(category='W')
        HB=Product.objects.filter(category='HB')
        S=Product.objects.filter(category='S')
        SF=Product.objects.filter(category='SF')
        TC=Product.objects.filter(category='TC')
        SM=Product.objects.filter(category='SM')
        DF=Product.objects.filter(category='DF')
        CM=Product.objects.filter(category='CM')
        KC=Product.objects.filter(category='KC')
        
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))

        context = {'Mobile':Mobile,'tablet':tablet,'WW':WW,'MW':MW, 'laptop': laptop, 'totalitem': totalitem,'PC':PC,'KC':KC,'TC':TC,'W':W,'toys':toys,'BabyCare':BabyCare,'DF':DF,'HB':HB}
        return render(request, 'app/home.html', context)


# @method_decorator(login_required, name='dispatch')
class ProductDetailView(View):
    def get(self, request, pk):
        totalitem = 0
        product = Product.objects.get(id=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(
                Q(product=product.id) & Q(user=request.user)).exists()
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/productdetail.html', {'product': product, 'item_already_in_cart': item_already_in_cart, 'totalitem': totalitem})

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('showcart')


@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        
        discount=0.0
        # list-comprehension
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        if cart_product:
            for p in cart_product:
            
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                if amount<500:
                    totalamount = amount + shipping_amount
                else :
                    totalamount=amount
                discount=discount+p.quantity*(p.product.selling_price-p.product.discounted_price)
            return render(request, 'app/addtocart.html', {'discount':discount,'carts': cart, 'totalamount': totalamount, 'amount': amount, 'totalitem': totalitem})
        else:
            return render(request, 'app/emptycart.html', {'totalitem': totalitem})


def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']

        # using get to extract single object
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()

        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        # list-comprehension
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]

        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)


def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']

        # using get to extract single object
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()

        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        # list-comprehension
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]

        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)


def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']

        # using get to extract single object
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()

        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        # list-comprehension
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]

        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)
@csrf_exempt
def remove_add(request,id):
    
    

        # using get to extract single object
    c = Customer.objects.get(Q(id=id) & Q(user=request.user))
    c.delete()
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'add': add})

    
       

def buy_now(request):
    return render(request, 'app/buynow.html')


# def profile(request):
#     return render(request, 'app/profile.html')


def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'add': add, 'active': 'btn-primary'})


@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'order_placed': op})


@login_required
def laptop(request, data=None):
    if data == None:
        laptop = Product.objects.filter(category='L')
    elif data == 'ASUS' or data == 'Apple' or data=='Dell' or data=='Acer'  or data=='HP':
        laptop = Product.objects.filter(category='L').filter(brand=data)
    elif data == 'above':
        laptop = Product.objects.filter(
            category='L').filter(discounted_price__gt=50000)
    elif data == 'below':
        laptop = Product.objects.filter(
            category='L').filter(discounted_price__lt=50000)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/laptop.html', {'laptop': laptop, 'totalitem': totalitem})

@login_required
def PC(request, data=None):
    if data == None:
        PC = Product.objects.filter(category='PC')
    elif data == 'above':
        PC= Product.objects.filter(
            category='PC').filter(discounted_price__gt=30000)
    elif data == 'below':
        PC= Product.objects.filter(
            category='PC').filter(discounted_price__lt=30000)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/PC.html', {'PC': PC, 'totalitem': totalitem})
@login_required
def mobile(request, data=None):
    if data == None:
        mobile = Product.objects.all().filter(category='M')
    elif data == 'Apple' or data == 'Oppo' or data=='Vivo' or data== 'Redmi' or data=='Samsung' :
        mobile = Product.objects.all().filter(category='M').filter(brand=data)
    elif data == 'above':
        mobile = Product.objects.all().filter(
            category='M').filter(discounted_price__gte=50000)
    elif data == 'below':
        mobile = Product.objects.all().filter(
            category='M').filter(discounted_price__lt=50000)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/mobile.html', {'mobile': mobile, 'totalitem': totalitem})

@login_required
def tablets(request, data=None):
    if data == None:
        tablets = Product.objects.all().filter(category='T')
    elif data == 'Apple'  or data=='Samsung' :
        tablets = Product.objects.all().filter(category='T').filter(brand=data)
    elif data == 'above':
        tablets = Product.objects.all().filter(
            category='T').filter(discounted_price__gte=50000)
    elif data == 'below':
        tablets= Product.objects.all().filter(
            category='T').filter(discounted_price__lt=50000)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/tablets.html', {'tablets': tablets, 'totalitem': totalitem})
@login_required
def camera(request, data=None):
    if data == None:
        camera = Product.objects.all().filter(category='C')
    elif data == 'Sony' or data == 'Canon' or data=='Nikon'  :
        camera= Product.objects.all().filter(category='C').filter(brand=data)
    elif data == 'above':
        camera= Product.objects.all().filter(
            category='C').filter(discounted_price__gte=50000)
    elif data == 'below':
        camera= Product.objects.all().filter(
            category='C').filter(discounted_price__lt=50000)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/camera.html', {'camera': camera, 'totalitem': totalitem})
@login_required
def tv(request, data=None):
    if data == None:
        tv = Product.objects.all().filter(category='TV')
    
    elif data == 'above':
        tv= Product.objects.all().filter(
            category='TV').filter(discounted_price__gte=50000)
    elif data == 'below':
        tv = Product.objects.all().filter(
            category='TV').filter(discounted_price__lt=50000)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/tv.html', {'tv': tv, 'totalitem': totalitem})
@login_required
def smart(request, data=None):
    if data == None:
        smart = Product.objects.all().filter(category='SW')
    
    elif data == 'above':
        smart= Product.objects.all().filter(
            category='SW').filter(discounted_price__gte=50000)
    elif data == 'below':
        smart = Product.objects.all().filter(
            category='SW').filter(discounted_price__lt=50000)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/smart.html', {'smart': smart, 'totalitem': totalitem})
@login_required
def health(request, data=None):
    if data == None:
        health = Product.objects.all().filter(category='HC')
   
    elif data == 'above':
        health= Product.objects.all().filter(
            category='HC').filter(discounted_price__gte=50000)
    elif data == 'below':
        health = Product.objects.all().filter(
            category='HC').filter(discounted_price__lt=50000)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/health.html', {'health': health, 'totalitem': totalitem})
@login_required
def cp(request, data=None):
    if data == None:
        cp = Product.objects.all().filter(category='CP')
    elif data == 'Sony'  or data=='Canon'  or data=='Nikon':
        cp = Product.objects.all().filter(category='C').filter(brand=data)
    elif data == 'above':
        cp= Product.objects.all().filter(
            category='CP').filter(discounted_price__gte=50000)
    elif data == 'below':
        cp = Product.objects.all().filter(
            category='CP').filter(discounted_price__lt=50000)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/cp.html', {'cp': cp, 'totalitem': totalitem})
@login_required
def kidsclothing(request, data=None):
    if data == None:
        KC= Product.objects.filter(category='KC')
    elif data == 'above':
        KC = Product.objects.filter(
            category='KC').filter(discounted_price__gt=500)
    elif data == 'below':
        KC= Product.objects.filter(
            category='KC').filter(discounted_price__lt=500)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/KC.html', {'KC': KC, 'totalitem': totalitem})

@login_required
def kidsfootwear(request, data=None):
    if data == None:
        KF= Product.objects.filter(category='KF')
    elif data == 'above':
        KF = Product.objects.filter(
            category='KF').filter(discounted_price__gt=30000)
    elif data == 'below':
        KF = Product.objects.filter(
            category='KF').filter(discounted_price__lt=30000)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/KF.html', {'KF': KF, 'totalitem': totalitem})
@login_required
def toys(request, data=None):
    if data == None:
        toys= Product.objects.filter(category='TO')
    elif data == 'above':
        toys = Product.objects.filter(
            category='TO').filter(discounted_price__gt=500)
    elif data == 'below':
        toys = Product.objects.filter(
            category='TO').filter(discounted_price__lt=500)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/toys.html', {'toys': toys, 'totalitem': totalitem})
@login_required
def BabyCare(request, data=None):
    if data == None:
        BC= Product.objects.filter(category='BC')
    elif data == 'above':
        BC = Product.objects.filter(
            category='BC').filter(discounted_price__gt=500)
    elif data == 'below':
        BC = Product.objects.filter(
            category='BC').filter(discounted_price__lt=500)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/BabyCare.html', {'BC': BC, 'totalitem': totalitem})
@login_required
def SchoolSupplies(request, data=None):
    if data == None:
        SS= Product.objects.filter(category='SS')
    elif data == 'above':
        SS= Product.objects.filter(
            category='SS').filter(discounted_price__gt=500)
    elif data == 'below':
        SS = Product.objects.filter(
            category='SS').filter(discounted_price__lt=500)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/SchoolSupplies.html', {'SS': SS, 'totalitem': totalitem})
@login_required
def Men(request, data=None):
    if data == None:
        MW= Product.objects.filter(category='MW')
    elif data == 'above':
        MW= Product.objects.filter(
            category='MW').filter(discounted_price__gt=500)
    elif data == 'below':
        MW= Product.objects.filter(
            category='MW').filter(discounted_price__lt=500)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/MenWear.html', {'MW': MW, 'totalitem': totalitem})
@login_required
def WomenWear(request, data=None):
    if data == None:
        WW= Product.objects.filter(category='WW')
    elif data == 'above':
        WW = Product.objects.filter(
            category='WW').filter(discounted_price__gt=500)
    elif data == 'below':
        WW= Product.objects.filter(
            category='WW').filter(discounted_price__lt=500)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/WomenWear.html', {'WW': WW, 'totalitem': totalitem})

@login_required
def Goggles(request, data=None):
    if data == None:
        G= Product.objects.filter(category='G')
    elif data == 'above':
        G= Product.objects.filter(
            category='G').filter(discounted_price__gt=500)
    elif data == 'below':
        G= Product.objects.filter(
            category='G').filter(discounted_price__lt=500)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/Goggles.html', {'G': G, 'totalitem': totalitem})

@login_required
def Watches(request, data=None):
    if data == None:
        W= Product.objects.filter(category='W')
    elif data == 'above':
        W = Product.objects.filter(
            category='W').filter(discounted_price__gt=500)
    elif data == 'below':
        W= Product.objects.filter(
            category='W').filter(discounted_price__lt=500)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/Watches.html', {'W': W, 'totalitem': totalitem})

@login_required
def HandBag(request, data=None):
    if data == None:
        HB= Product.objects.filter(category='HB')
    elif data == 'above':
        HB = Product.objects.filter(
            category='HB').filter(discounted_price__gt=500)
    elif data == 'below':
        HB= Product.objects.filter(
            category='HB').filter(discounted_price__lt=500)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/HandBag.html', {'HB': HB, 'totalitem': totalitem})

@login_required
def ShoesSandals(request, data=None):
    if data == None:
        S= Product.objects.filter(category='S')
    elif data == 'above':
        S = Product.objects.filter(
            category='S').filter(discounted_price__gt=500)
    elif data == 'below':
        S= Product.objects.filter(
            category='S').filter(discounted_price__lt=500)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/ShoesSandals.html', {'S': S, 'totalitem': totalitem})

@login_required
def SnackFood(request, data=None):
    if data == None:
        SF= Product.objects.filter(category='SF')
    elif data == 'above':
        SF = Product.objects.filter(
            category='SF').filter(discounted_price__gt=500)
    elif data == 'below':
        SF= Product.objects.filter(
            category='SF').filter(discounted_price__lt=500)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/SnackFood.html', {'SF': SF, 'totalitem': totalitem})

@login_required
def TeaCoffee(request, data=None):
    if data == None:
        TC= Product.objects.filter(category='TC')
    elif data == 'above':
        TC = Product.objects.filter(
            category='TC').filter(discounted_price__gt=500)
    elif data == 'below':
        TC= Product.objects.filter(
            category='TC').filter(discounted_price__lt=500)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/TeaCoffee.html', {'TC': TC, 'totalitem': totalitem})
@login_required
def SpicesMasala(request, data=None):
    if data == None:
        SM= Product.objects.filter(category='SM')
    elif data == 'above':
        SM = Product.objects.filter(
            category='SM').filter(discounted_price__gt=500)
    elif data == 'below':
        SM= Product.objects.filter(
            category='SM').filter(discounted_price__lt=500)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/SpicesMasala.html', {'SM': SM, 'totalitem': totalitem})

@login_required
def DriedFruitNuts(request, data=None):
    if data == None:
        DF= Product.objects.filter(category='DF')
    elif data == 'above':
        DF = Product.objects.filter(
            category='DF').filter(discounted_price__gt=500)
    elif data == 'below':
        DF= Product.objects.filter(
            category='DF').filter(discounted_price__lt=500)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/DriedFruits.html', {'DF': DF, 'totalitem': totalitem})

@login_required
def Cerial(request, data=None):
    if data == None:
        CM= Product.objects.filter(category='CM')
    elif data == 'above':
        CM = Product.objects.filter(
            category='CM').filter(discounted_price__gt=500)
    elif data == 'below':
        CM= Product.objects.filter(
            category='CM').filter(discounted_price__lt=500)

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'app/cerial.html', {'CM': CM, 'totalitem': totalitem})


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(
                request, 'Congratulations!! Registered Successfully')
            form.save()
        return render(request, 'app/customerregistration.html', {'form': form})




@login_required
def checkout(request):

    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    transaction_id=random.randint(1,100000)
    print(user)
    amount = 0.0
    shipping_amount = 70.0
    totalamount = 0.0

    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    k=0
    '''for i in Product.objects.all():
        i.quantity_available=random.randrange(1,200)
        i.save()
    
    for i in Product.objects.all():
        i.ratings=random.randrange(2,6)
        i.save()
    
    for i in Product.objects.all():
        i.offer=random.choice([True, False])
        i.save()
    
    for i in Product.objects.all():
        if i.offer:
            i.offer_value=random.randrange(10,60)
        i.save()
    '''
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            t = Product.objects.get(id=p.product.id)
            if t.quantity_available>0:
                t.quantity_available=t.quantity_available-p.quantity
                t.save()
            
            amount += tempamount
        if amount<500:
            totalamount = amount + shipping_amount
        else:
            totalamount=amount
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
  
    return render(request, 'app/checkout.html', {'transaction_id':transaction_id,'amount':amount,'add': add, 'totalamount': totalamount, 'cart_items': cart_items, 'totalitem': totalitem})

@login_required
def payment_done(request):

    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    
    for c in cart:
        OrderPlaced(user=user, customer=customer,transaction_id=transaction_id,
                    product=c.product, quantity=c.quantity).save()
        
        
        c.delete()
    return redirect("orders")


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary', 'totalitem': totalitem})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=user, name=name, locality=locality,
                           city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(
                request, 'Congratulations Profile Updated Successfully!!')
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary', 'totalitem': totalitem})

def ratings(request):
    return render(request,'app/ratings.html')
def search(request):
    # here 'search' is name in input tag in base.html
    data = request.GET['search']
    
    if (data.lower()) == 'mobile':
        return redirect('mobile')
    elif data.lower() == 'laptop':
        return redirect('laptop')
    elif data.lower() == 'kids clothing':
        return redirect('KC')
    elif data.lower() == 'goggles':
        return redirect('G')
        
    else:
        return redirect('home')        

