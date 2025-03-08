import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
import uuid

class PaymentTicket(models.Model):
    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
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
        return f"Ticket {self.ticket_id} - {self.user.username} - {self.amount}"
