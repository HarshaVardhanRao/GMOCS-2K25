from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Category, Events, registrations, PaymentTicket
from .forms import RegistrationForm
from datetime import timedelta,datetime
import time
from django.views.decorators.csrf import csrf_exempt
import json

UPI_ID = "hvijapuram-3@okaxis"

def index(request):
    if request.method == "POST":
        roll = request.POST.get("roll")
        regs = registrations.objects.filter(roll_no = roll)
        print("registrations",regs)
        return render(request,'users.html',{'registrations':regs})

    return render(request, 'index.html')

def mobile_view(request):
    if request.method == "POST":
        roll = request.POST.get("roll")
        regs = registrations.objects.filter(roll_no = roll)
        print("registrations",regs)
        return render(request,'users.html',{'registrations':regs})

    return render(request, 'mobile.html')

def event_list(request):
    categories = Category.objects.all()
    events = Events.objects.all()
    return render(request, 'events.html', {'categories': categories, 'events': events})

@csrf_exempt
def register_event(request):
    

    if request.method == "POST":
        print(request.body)
        data = json.loads(request.body)
        {'name': 'V Mahesh Kumar', 'mobile': '9398983918', 'rollno': '22691A05B5', 'branch': 'CSE', 'members': [], 'college': 'MITS', 'eventName': 'Movie Mania', 'teamSize': 1, 'utr': '2345908978'}
        print(data)
        new_registration = registrations()
        new_registration.username = data['name']
        new_registration.roll_no = data['rollno']
        new_registration.phone = data['mobile']
        new_registration.branch = data['branch']
        new_registration.event = Events.objects.filter(id=data['eventId'])[0]
        new_registration.members = data['members']
        new_registration.utr = data['utr']
        print(new_registration)
        new_registration.save()
        return JsonResponse(json.dumps(data), safe=False)

    return JsonResponse({"message": "GET Method"})

@login_required
def registration_list(request):
    if request.user.is_superuser:
    # Get the search parameters
        search_date = request.GET.get('search_date')
        print(search_date)
        category_id = request.GET.get('category')  # Get the category from the query parameters
        if search_date == '':
            search_date = None
        # Retrieve all registrations by default
        regs = registrations.objects.all()

        # Filter registrations by date if provided
        if search_date:
            try:
                date_object = datetime.strptime(search_date, '%Y-%m-%d').date()
                regs = regs.filter(registered_on=date_object)
            except ValueError:
                pass

        # Filter registrations by category if provided
        if category_id:
            regs = regs.filter(event__category_id=category_id)

        # Handle CSV download
        if "download" in request.GET:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="registrations.csv"'

            writer = csv.writer(response)
            writer.writerow(['Name', 'Roll Number', 'Year', 'Branch', 'Section', 'Email', 'Mobile Number', 'Event', 'Date'])
            for reg in regs:
                writer.writerow([
                    reg.name, reg.roll_number, reg.year, reg.branch, reg.section,
                    reg.email, reg.mobile_number, reg.event.name, reg.registered_on
                ])
            return response

        # Retrieve all categories for the filter dropdown
        categories = Category.objects.all()

        context = {
            'registrations': regs,
            'search_date': search_date,
            'categories': categories,
            'selected_category': category_id,
        }
        return render(request, 'registrations.html', context)
    elif request.user.is_authenticated:
        
        event = Events.objects.filter(coordinator=request.user.id).first()
        regs = registrations.objects.filter(event=event)
        return render(request, 'registrations.html', {'registrations': regs})
    else:
        return redirect('login')
    
from django.contrib.auth import authenticate, login,logout
def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request,user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


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

from django.http import JsonResponse
import os
import hmac
import subprocess
import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings

GITHUB_SECRET = b"Thisissecretcode"

def verify_signature(payload, signature):
    mac = hmac.new(GITHUB_SECRET, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest("sha256=" + mac, signature)

@csrf_exempt
def deploy_view(request):
    if request.method == "POST":
        signature = request.headers.get("X-Hub-Signature-256")

        # Validate the request
        if not signature or not verify_signature(request.body, signature):
            return JsonResponse({"error": "Unauthorized"}, status=403)

        try:
            # Pull the latest code
            repo_path = "/home/gmocs/GMOCS-2K25/gmocs2k25"
            subprocess.run(["git", "-C", repo_path, "pull", "origin", "master"], check=True)

            return JsonResponse({"status": "Success", "message": "Deployment complete!"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Unexpected Error"}, status = 500)

# Just Updated

def hello(request):
    return HttpResponse("<h1>Hello Developer</h1>")