from django.db import models
from gym.models import Branch
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

class Equipment(models.Model):
    name = models.CharField(max_length=100,unique=True)
    description = models.TextField()
    url = models.URLField(blank=True)
    qr_code_image = models.ImageField(upload_to='qr_codes', null=True, blank=True)

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

        file_name = f"{self.name.replace(' ', '_')}.png"
        self.qr_code_image.save(file_name, ContentFile(qr_file.getvalue()), save=False)


    def save(self, *args, **kwargs):
        if self.url:
            self.generate_qr_code(self.url)
        super().save(*args, **kwargs)

class Diagram(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="diagrams")
    floor = models.IntegerField(default=0)

class Diagrams_Equipments(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="diagrams")
    diagram = models.ForeignKey(Diagram, on_delete=models.CASCADE, related_name="equipment")
    status = models.BooleanField(default=True)
    x_axis = models.FloatField(default=0.0)
    y_axis = models.FloatField(default=0.0)
    is_deleted = models.BooleanField(default=False)

    
class Exercise(models.Model):
    name = models.CharField(max_length=50 , unique=True)
    description = models.TextField(max_length=100)
    muscle_group = models.CharField(max_length=50)
    
class Equipment_Exercise(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="equipment")
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="exercise")
    video_path = models.FileField(upload_to='videos/',null=True)