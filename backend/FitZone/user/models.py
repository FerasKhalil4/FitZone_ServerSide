from django.db import models
from django.contrib.auth.models import User 
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name="client") 
    points = models.IntegerField(default=0)
    wakeup_time = models.TimeField(null = True)
    height = models.FloatField(default=0.0)
    app_rate = models.IntegerField(null = True)
    address = models.CharField(null = True)
    qr_code_image = models.ImageField(upload_to = 'qr_codes',null = True)
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

        file_name = f"{self.name.replace(' ', '_')}.png"
        self.qr_code_image.save(file_name, ContentFile(qr_file.getvalue()), save=False)
    

    def save(self, *args, **kwargs):
        if self.user.usermame and self.pk:
            data = {'id':self.pk , 'username': self.user.username }
            self.generate_qr_code(data)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.user:
            self.user.is_deleted = True
            self.user.save()
        # super(Client, self).delete(*args, **kwargs) delete the record

class Goal (models.Model):
    client = models.ForeignKey(Client , on_delete=models.CASCADE , related_name= "history")
    weight =models.FloatField(default=0.0)
    goal = models.CharField(max_length=50)
    goal_weight = models.FloatField(default=0.0)
    predicted_date = models.DateField(blank=True)
    created_at = models.DateField(auto_now_add=True)
    

    