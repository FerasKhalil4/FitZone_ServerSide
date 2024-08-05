from django.db import models
from gym.models import Branch, Trainer
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models import UniqueConstraint

class Equipment(models.Model):
    name = models.CharField(max_length=100,unique=True)
    description = models.TextField()
    url = models.URLField(blank=True)
    qr_code_image = models.ImageField(upload_to='qr_codes', null=True, blank=True)
    image_path = models.ImageField(upload_to='image', null=True)

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
    def __str__(self) -> str:
        return self.name

class Diagram(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="diagrams")
    floor = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    width = models.IntegerField(default=0)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=('branch','floor'),name=('branch_floor'))
        ]

class Diagrams_Equipments(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="diagrams")
    diagram = models.ForeignKey(Diagram, on_delete=models.CASCADE, related_name="equipment")
    status = models.BooleanField(default=True)
    x_axis = models.FloatField(default=0.0)
    y_axis = models.FloatField(default=0.0)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=('diagram','x_axis','y_axis'),name=('diagram_axises'))
        ]

class Exercise(models.Model):
    name = models.CharField(max_length=50 , unique=True)
    description = models.TextField(max_length=100)
    muscle_group = models.CharField(max_length=50)
    
class Equipment_Exercise(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="equipment")
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="exercise")
    video_path = models.FileField(upload_to='videos/',null=True)
    trainer = models.ForeignKey(Trainer,on_delete=models.CASCADE, related_name="exercises",null=True)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['equipment', 'exercise','trainer'], name='unique_exercises_equipments')
        ]