from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Category, Events, RegisteredUser, registrations, PaymentTicket
from .forms import RegistrationForm
from datetime import timedelta

UPI_ID = "hvijapuram-3@okaxis"

def index(request):
    return render(request, 'index.html')

def event_list(request):
    categories = Category.objects.all()
    events = Events.objects.all()
    return render(request, 'events.html', {'categories': categories, 'events': events})

def register_event(request, event_id):
    event = get_object_or_404(Events, id=event_id)

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            payment_ticket = PaymentTicket.objects.create(
                amount=event.price,
                expires_at=timezone.now() + timedelta(hours=24)
            )

            payment_ticket.generate_qr(UPI_ID)

            registrations.objects.create(user=user, event=event, Payment=payment_ticket)

            return redirect('ticket_detail', ticket_id=payment_ticket.ticket_id)

    else:
        form = RegistrationForm()

    return render(request, 'register_event.html', {'form': form, 'event': event})


################### Tickets ######################
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
