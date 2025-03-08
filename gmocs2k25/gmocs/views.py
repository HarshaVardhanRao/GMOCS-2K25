from django.utils import timezone
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import PaymentTicket
from datetime import timedelta

# Create your views here.

def index(request):
    return render(request, 'index.html')



UPI_ID = "hvijapuram-3@okaxis"

@login_required
def generate_ticket(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        ticket = PaymentTicket.objects.create(
            user=request.user,
            amount=amount,
            expires_at=timezone.now() + timedelta(days=1)
        )
        ticket.generate_qr(UPI_ID)
        ticket.save()
        return redirect('ticket_detail', ticket_id=ticket.ticket_id)

    return render(request, 'generate_ticket.html')



def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(PaymentTicket, ticket_id=ticket_id)
    return render(request, 'ticket_detail.html', {'ticket': ticket})



def confirm_payment(request, ticket_id):
    ticket = get_object_or_404(PaymentTicket, ticket_id=ticket_id)

    if request.method == "POST":
        transaction_id = request.POST.get("transaction_id")
        if transaction_id:
            ticket.upi_transaction_id = transaction_id
            ticket.status = "paid"
            ticket.save()
            return redirect('ticket_detail', ticket_id=ticket.ticket_id)

    return render(request, 'confirm_payment.html', {"ticket": ticket})

