from django.db import models
from user.models import User
from django.db.models import UniqueConstraint
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

class Gym(models.Model):
    name = models.CharField(max_length=30 , unique=True)
    description = models.TextField(max_length=100 , null = True)
    image_path = models.ImageField(upload_to='images/' , null= True)
    created_at = models.DateTimeField(auto_now_add=True)
    allow_retrival = models.BooleanField(default=False)
    duration_allowed = models.IntegerField(null = True)
    cut_percentage = models.FloatField(null = True)
    is_deleted = models.BooleanField(default=False)
    start_hour = models.TimeField()
    close_hour = models.TimeField()
    mid_day_hour = models.TimeField()
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='manager')
    allow_public_posts = models.BooleanField(default=True)
    allow_public_products = models.BooleanField(default=True)
    allowed_days_for_registraiton_cancellation = models.IntegerField(default=0)
    allow_branches_access = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.id}:{self.name}"
    
    
class Registration_Fee(models.Model):
    TYPE_CHOICES = [
        ('1_day','1_day'),
        ('15_days','15_days'),
        ('monthly','monthly'),
        ('3_months','3_months'),
        ('6_months','6_months'),
        ('yearly','yearly'),
    ]
    gym = models.ForeignKey(Gym , on_delete=models.CASCADE,related_name="fees" )
    type = models.CharField(max_length=50,choices=TYPE_CHOICES)
    fee = models.FloatField(default = 0.0)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=('gym','type'), name='gym_type'),
        ]
    
class Woman_Training_Hours(models.Model):
    gym = models.ForeignKey(Gym , on_delete=models.CASCADE,related_name="woman_gym" )
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    day_of_week = models.CharField()
    
class Branch(models.Model):
    gym = models.ForeignKey(Gym , on_delete=models.CASCADE,related_name="gym" )
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=50, blank = True)
    street = models.CharField(max_length=50,blank = True)
    has_store = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    url = models.URLField(blank=True)
    qr_code_image = models.ImageField(upload_to='qr_codes', null=True, blank=True)
    number_of_clients_allowed = models.IntegerField(default=0)
    current_number_of_clients= models.IntegerField(default=0)
    
    def generate_qr_code(self,data):
        url = data
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        image = qr.make_image(fill_color="black", back_color="white")

        qr_file = BytesIO()
        image.save(qr_file, format="PNG")

        file_name = f"{self.gym.name.replace(' ', '_')}.png"
        self.qr_code_image.save(file_name, ContentFile(qr_file.getvalue()), save=False)


    def save(self, *args, **kwargs):
        if self.url:
            self.generate_qr_code(self.url)
        super().save(*args, **kwargs)
    
    def delete(self , *args , **kwargs):
        if self:
            self.is_active = False
            self.save()
    
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name="user") 
    is_trainer = models.BooleanField(default=False)

class Trainer(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="trainer")
    allow_public_posts = models.BooleanField(default=True)
    private_training_price = models.FloatField(default=0.00)
    online_training_price = models.FloatField(default=0.00)
    

    
class Shifts (models.Model):
    employee = models.ForeignKey(Employee , on_delete=models.CASCADE, related_name="employee")
    branch = models.ForeignKey(Branch , on_delete=models.CASCADE,related_name="branch")
    shift_type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    days_off = models.JSONField(default = dict)
    

    