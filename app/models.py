from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

STATE_CHOICES = (
    ('Andaman & Nicobar Islands', 'Andaman & Nicobar Islands'),
    ('Andra Pradesh', 'Andra Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('U.P', 'U.P'),
    ('M.P', 'M.P'),
    ('Delhi', 'Delhi'),
    ('Maharastra','Maharastra'),
    ('Madhya Pradesh','Madhya Pradesh')

)

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    zipcode = models.IntegerField()
    state = models.CharField(choices = STATE_CHOICES, max_length=200)

    def __str__(self):
        return str(self.id)

CATEGORY_CHOICES = (
    ('M', 'Mobile'),
    ('L', 'Laptop'),
    ('T','Tablet'),
    ('TW', 'Top Wear'),
    ('BW', 'Bottom Wear'),
    ('C','Camera'),
    ('TV','TV'),
    ('PC','PC'),
    ('SW','Smart Wearable Tech'),
    ('HC','Health Care Appliances'),
    ('CP','Computer Peripherals'),
    ('KC','Kids Clothing'),
    ('KF','Kids Footwear'),
    ('TO','Toys'),
    ('BC','Baby Care'),
    ('SS','School Supplies'),
    ('G','Grocerries'),
    ('TG','Toys & Games Store'),
    ('MW','Mens Wear'),
    ('WW','Womens Wear'),
    ('G','Goggles'),
    ('W','Watches'),
    ('HB','HandBag and Clutches'),
    ('S','Shoes and Sandals'),
    ('SF','Snack Food'),
    ('TC','Tea , Coffee and Beverages'),
    ('SM','Spices and Masala'),
    ('DF','Dried Fruits and Nuts'),
    ('CM','Cerial and Muesli')
)   

class Product(models.Model):
    title = models.CharField(max_length=200)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    brand = models.CharField(max_length=200)
    category = models.CharField(choices = CATEGORY_CHOICES, max_length=2)
    product_image = models.ImageField(upload_to = 'productimg')
    quantity_available=models.IntegerField(default=100)
    ratings=models.IntegerField(default =5)
    offer=models.BooleanField(default=False)
    offer_value=models.IntegerField(default=10)
    def __str__(self):
        return str(self.id)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField(default=1) 

    def __str__(self):
        return str(self.id)

    # helps in model template relationship
    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price        

STATUS_CHOICES = (
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On The Way', 'On The Way'),
    ('Delivered', 'Delivered'),
    ('Cancel', 'Cancel')
)  

class OrderPlaced(models.Model):
    transaction_id=models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField(default=1) 
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')



    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price        

class PaytmDataBase(models.Model):
    
    order_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=7, decimal_places=2) # 99999.99
    checksumhash = models.CharField(max_length=255)
    txn_id = models.CharField(max_length=100)
    status=models.CharField(max_length=50)
    txndate=models.CharField(max_length=255)
    banktxnid=models.CharField(max_length=255)

    def __str__(self):
        return str(self.order_id)