import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
import uuid
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

class upiid(models.Model):
    upiId = models.CharField(max_length=50)

class PaymentTicket(models.Model):
    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    upi_transaction_id = models.CharField(max_length=50, blank=True, null=True)

    def generate_qr(self, upi_id):
        upi_link = f"upi://pay?pa={upi_id}&am={self.amount}&cu=INR"
        #upi://pay?pa={upi_id}&pn=Merchant&mc=1234&tid={self.ticket_id}&tr={self.ticket_id}&tn=Payment&am={self.amount}&cu=INR
        qr = qrcode.make(upi_link)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        self.qr_code.save(f"{self.ticket_id}.png", ContentFile(buffer.getvalue()), save=True)
        buffer.close()

    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.amount}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.name}"
    
def get_default_coordinator():
    return User.objects.filter(is_superuser=False).first().id  # Picks the first non-superuser



class Events(models.Model):
    Category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date = models.DateTimeField()
    location = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    price = models.IntegerField()
    coordinator = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='coordinator', default=get_default_coordinator, blank=True, null=True
    )

    def __str__(self):
        return f"{self.name}"



class registrations(models.Model):
    username = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    branch = models.CharField(max_length=20)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    utr = models.CharField(max_length=20,unique=True)
    STATUS_CHOICES = [("Pending", "Pending"), ("Rejected", "Rejected"), ("Approved","Approved")]
    status = models.CharField(choices=STATUS_CHOICES, max_length=15, default="Pending")
    members = models.JSONField(default=list,null=True, blank=True)
    college = models.CharField(max_length=100, default="MITS")
    PARTICIPATION_MODE_CHOICES = [("Online", "Online"), ("Offline", "Offline"), ("Freefire", "Freefire"), ("BGMI", "BGMI"), ("Ludo", "Ludo")]
    participation_mode = models.CharField(choices=PARTICIPATION_MODE_CHOICES, max_length=10, default="Offline")
    registred_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.roll_no} - {self.event.name}"


class PrintJob(models.Model):
    ORIENTATION_CHOICES = [
        ('portrait', 'Portrait'),
        ('landscape', 'Landscape')
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='print_files/')
    copies = models.PositiveIntegerField(default=1)
    orientation = models.CharField(max_length=20, choices=ORIENTATION_CHOICES, default='portrait')
    pages_per_sheet = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Print job by {self.user.username} - {self.status}"