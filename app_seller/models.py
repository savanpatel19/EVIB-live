from django.db import models

# Create your models here.
class seller_user(models.Model):
    seller_fullname=models.CharField(max_length=50)
    seller_username=models.EmailField(unique=True)
    seller_password=models.CharField(max_length=50)
    
    def __str__(self)  :
        return  self.seller_fullname
    
    
    
class Product(models.Model):
    pname=models.CharField(max_length=50)
    price=models.CharField(max_length=10)   
    desc=models.CharField(max_length=200)
    pimage=models.FileField(upload_to='pimage',default='productimage.jpeg')
    seller=models.ForeignKey(seller_user,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.pname
