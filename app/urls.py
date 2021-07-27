from django.urls import path,include
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from .forms import LoginForm, MyPasswordChangeForm, MyPasswordResetForm, MySetPasswordForm
from .views import (PaytmRequest, PaytmResponse, 
                    paytm_transection_status, TestPaytm)

urlpatterns = [
    path('mail',views.mail)  ,
    path('', views.ProductView.as_view(), name='home'),
   path('ratings/', views.ratings, name='ratings'),
    path('product-detail/<int:pk>',
         views.ProductDetailView.as_view(), name='product-detail'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('cart/', views.show_cart, name='showcart'),
    path('pluscart/', views.plus_cart, name='pluscart'),
    path('minuscart/', views.minus_cart, name='minuscart'),
    path('removecart/', views.remove_cart, name='removecart'),
  
    path('removeadd/<int:id>/',views.remove_add,name='removeadd'),

    path('buy/', views.buy_now, name='buy-now'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('address/', views.address, name='address'),
    path('orders/', views.orders, name='orders'),
    path('laptop/', views.laptop, name='laptop'),
    path('PC/', views.PC, name='PC'),
    path('PC/<slug:data>', views.PC, name='PCdata'),
    path('laptop/<slug:data>', views.laptop, name='laptopdata'),
    path('camera/', views.camera, name='camera'),
    path('camera/<slug:data>', views.camera, name='cameradata'),
    path('tv/', views.tv, name='tv'),
    path('tv/<slug:data>', views.tv, name='tvdata'),
    path('smart/', views.smart, name='smart'),
    path('smart/<slug:data>', views.smart, name='smartdata'),
    path('health/', views.health, name='health'),
    path('health/<slug:data>', views.health, name='healthdata'),
    path('cp/', views.cp, name='cp'),
    path('cp/<slug:data>', views.cp, name='cpdata'),
    path('mobile/', views.mobile, name='mobile'),
    path('mobile/<slug:data>', views.mobile, name='mobiledata'),
    path('tablets/', views.tablets, name='tablets'),
    path('tablets/<slug:data>', views.tablets, name='tabletsdata'),
    path('KC',views.kidsclothing,name='KC'),
    path('KC/<slug:data>', views.kidsclothing, name='KCdata'),
    path('KF',views.kidsfootwear,name='KF'),
    path('KF/<slug:data>', views.kidsfootwear, name='KFdata'),
    path('TO',views.toys,name='TO'),
    path('TO/<slug:data>', views.toys, name='TOdata'),
    path('BC',views.BabyCare,name='BC'),
    path('BC/<slug:data>', views.BabyCare, name='BCdata'),
    path('SS',views.SchoolSupplies,name='SS'),
    path('SS/<slug:data>',views.SchoolSupplies , name='SSdata'),
    path('MW',views.Men,name='MW'),
    path('MW/<slug:data>',views.Men , name='MWdata'),
    path('WW',views.WomenWear,name='WW'),
    path('WW/<slug:data>',views.WomenWear , name='WWdata'),
    path('G',views.Goggles,name='G'),
    path('G/<slug:data>',views.Goggles , name='Gdata'),
    path('W',views.Watches,name='W'),
    path('W/<slug:data>',views.Watches , name='Wdata'),
    path('HB',views.HandBag,name='HB'),
    path('HB/<slug:data>',views.HandBag , name='HBdata'),
    path('S',views.ShoesSandals,name='S'),
    path('S/<slug:data>',views.ShoesSandals , name='Sdata'),
    path('SF',views.SnackFood,name='SF'),
    path('SF/<slug:data>',views.SnackFood , name='SFdata'),
    path('TC',views.TeaCoffee,name='TC'),
    path('TC/<slug:data>',views.SnackFood , name='TCdata'),
    path('SM',views.SpicesMasala,name='SM'),
    path('SM/<slug:data>',views.SpicesMasala, name='SMdata'),
    path('DF',views.DriedFruitNuts,name='DF'),
    path('DF/<slug:data>',views.DriedFruitNuts , name='DFdata'),
    path('CM',views.Cerial,name='CM'),
    path('CM/<slug:data>',views.Cerial, name='CMdata'),

    path('checkout/', views.checkout, name='checkout'),
    path('paymentdone/', views.payment_done, name='paymentdone'),
    #path('paytm/', include('paytm.urls')),
    
    path('paytm/',PaytmRequest.as_view()),
    path('paytm/test/', TestPaytm.as_view()),
    path('paytm/payment_response/', PaytmResponse.as_view()),
    path('paytm/status/', paytm_transection_status),

    # ------------- Authentication Starts Here ----------    
    # 3:42:00 ends  
    # Password change done view used in urls only, no such views exist in views.py
    
    path('accounts/login/', auth_views.LoginView.as_view(template_name='app/login.html',
                                                         authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('passwordchange/', auth_views.PasswordChangeView.as_view(template_name='app/passwordchange.html',
                                                                  form_class=MyPasswordChangeForm, success_url='/passwordchangedone/'), name='passwordchange'),
    path('passwordchangedone/', auth_views.PasswordChangeView.as_view(
        template_name='app/passwordchangedone.html'), name='passwordchangedone'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='app/password_reset.html',
                                                                 form_class=MyPasswordResetForm), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='app/password_reset_done.html'), name='password_reset_done'),


    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='app/password_reset_confirm.html', form_class=MySetPasswordForm), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='app/password_reset_complete.html'), name='password_reset_complete'),
    # ------------- Authentication Ends Here ----------   



    path('registration/', views.CustomerRegistrationView.as_view(),
         name='customerregistration'),

   # -------------search functionality--------------------
    path('search', views.search, name='search')      
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
