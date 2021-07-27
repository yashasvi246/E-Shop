from django.contrib import admin

# Register your models here.
from .models import *
from .models import PaytmDataBase #,PaytmRefundDataBase
# Register your models here.
@admin.register(PaytmDataBase)
class PaytmDataBaseAdmin(admin.ModelAdmin):
    list_display = ('order_id','amount', 'txn_id','status','txndate','banktxnid')
@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display=['id','title' ,'selling_price' ,'discounted_price', 'description' , 'brand' ,  'category' ,'product_image' ,'quantity_available','ratings','offer','offer_value']

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display=['id','user','name', 'locality','city','zipcode','state']
@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display=['user' ,'product' ,'quantity']
@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display=['transaction_id','order_id','user' ,'customer' ,'product','quantity' ,'ordered_date' ,'status']