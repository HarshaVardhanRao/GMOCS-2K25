from django.contrib import admin
from gmocs.models import PaymentTicket,Events,Category

# Register your models here.
admin.site.register(PaymentTicket)
admin.site.register(Events)
admin.site.register(Category)