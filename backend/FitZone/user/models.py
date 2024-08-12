from django.db import models
from django.apps import apps
from django.contrib.auth.models import User 
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import datetime

class Client(models.Model):    
    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name="client") 
    points = models.IntegerField(default=0)
    height = models.FloatField(default=0.0)
    app_rate = models.IntegerField(null = True)
    address = models.CharField(null = True)
    qr_code_image = models.ImageField(upload_to = 'qr_codes',null = True)
    url = models.URLField(blank=True)
    image_path = models.ImageField(upload_to = 'images/',null = True)
    
    
    
    def generate_qr_code(self,data):
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        image = qr.make_image(fill_color="black", back_color="white")

        qr_file = BytesIO()
        image.save(qr_file, format="PNG")

        file_name = f"{self.user.username.replace(' ', '_')}.png"
        self.qr_code_image.save(file_name, ContentFile(qr_file.getvalue()), save=False)
    

    def save(self, *args, **kwargs):
        if self.url:
            data = self.url
            self.generate_qr_code(data)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.user:
            self.user.is_deleted = True
            self.user.save()

class Goal (models.Model):    
    MAX_UPDATES = 3
    ACTIVITY_LEVEL =[
        ('Low', 'Low'),
        ('Moderate', 'Moderate'),
        ('High', 'High'),
    ] 
    
    client = models.ForeignKey(Client , on_delete=models.CASCADE , related_name= "history")
    weight =models.FloatField(default=0.0)
    goal = models.CharField(max_length=50)
    goal_weight = models.FloatField(default=0.0)
    predicted_date = models.DateField(blank=True)
    created_at = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Active')
    is_deleted = models.BooleanField(default=False)
    number_updates = models.PositiveIntegerField(default=MAX_UPDATES)
    achieved_weight=  models.FloatField(null=True)
    activity_level = models.CharField(max_length=20,choices=ACTIVITY_LEVEL)
    protein_required = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    fats_required = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    calories_required = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    
    def get_age(self):
        birth_date = self.client.user.birth_date
        today = datetime.datetime.now().date()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))    
        return age    
    
    def calculate_nutritional_requirements(self):
            
        def calculate_male_maintenance(weight_kg, height_cm, age, goal, activity_level):
    
            calories = 66.47 + (13.75 * weight_kg) + (5.0 * height_cm) - (6.75 * age)
            
            if goal == "Lose Weight":
                if activity_level == "Low":
                    calories -= 500  
                elif activity_level == "Moderate":
                    calories -= 750  
                elif activity_level == "High":
                    calories -= 1000
            elif goal == "Gain Weight":
                if activity_level == "Low":
                    calories += 300 
                elif activity_level == "Moderate":
                    calories += 500
                elif activity_level == "High":
                    calories += 750 
            
            return calories

        def calculate_female_maintenance(weight_kg, height_cm, age, goal, activity_level):

            calories = 655.1 + (9.56 * weight_kg) + (1.85 * height_cm) - (4.68 * age)
            
            if goal == "Lose Weight":
                if activity_level == "Low":
                    calories -= 400 
                elif activity_level == "Moderate":
                    calories -= 600  
                elif activity_level == "High":
                    calories -= 800 
            elif goal == "Gain Weight":
                if activity_level == "Low":
                    calories += 250 
                elif activity_level == "Moderate":
                    calories += 400  
                elif activity_level == "High":
                    calories += 600 
            return calories
        def calculate_protein_requirement(weight_kg, activity_level):

            if activity_level == "Low":
                protein_grams = weight_kg * 0.8 
            elif activity_level == "Moderate":
                protein_grams = weight_kg * 1.4
            elif activity_level == "High":
                protein_grams = weight_kg * 1.8 
            
            return protein_grams
        def calculate_fat_requirement(calories):
            if self.goal == 'Lose Weight':
                fat_percentage = 0.20 
            elif self.goal == 'Gain Weight':
                fat_percentage = 0.35
            elif self.goal == 'Maintain Weight':
                fat_percentage = 0.30
            calories_from_fat = calories * fat_percentage
            fat_grams = calories_from_fat / 9 
            return fat_grams    
          
        weight = self.weight
        height = self.client.height
        age = self.get_age()
        goal = self.goal
        activity_level = self.activity_level
        if self.client.user.gender:
            self.calories_required = calculate_male_maintenance(weight, height, age, goal, activity_level)
        else:
            self.calories_required = calculate_female_maintenance(weight, height, age, goal, activity_level)
        self.protein_required = calculate_protein_requirement(weight, activity_level)
        self.fats_required = calculate_fat_requirement(self.calories_required)
        
    def save(self, *args, **kwargs):
        if self.number_updates is None:
            self.number_updates = self.MAX_UPDATES
        self.calculate_nutritional_requirements()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self:
            self.is_deleted = True
            self.save()
