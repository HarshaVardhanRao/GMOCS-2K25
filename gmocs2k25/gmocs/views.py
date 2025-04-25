from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Category, Events, registrations, PaymentTicket, PrintJob
from .forms import RegistrationForm
from datetime import timedelta,datetime
import time
import csv
import cups
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import IntegrityError

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

def committee(request):
    return render(request, 'committee.html')

def sponsers(request):
    return render(request, 'sponsers.html')

@csrf_exempt
def register_event(request):
    if request.method == "POST":
        try:
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
            new_registration.college = data['college']
            if data['modeOfAttendance']:
                new_registration.participation_mode = data['modeOfAttendance']
            new_registration.members = data['members']
            new_registration.utr = data['utr']
            print(new_registration)
            new_registration.save()
            print("saved")
            return JsonResponse({"message": "Registred Successfully"}, safe=False)
        except IntegrityError:
            print("error")
            return JsonResponse({"message": "You can't cheat me.......UTR already exists"})

    return JsonResponse({"message": "GET Method"})

@login_required
def registration_list(request):
    if request.user.is_superuser:
    # Get the search parameters
        search_date = request.GET.get('search_date')
        print(search_date)
        event_id = request.GET.get('event')  # Get the category from the query parameters
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
        if event_id:
            regs = regs.filter(event__id=event_id)

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

        # Retrieve all categories for the filter dropdown\
        events = Events.objects.all()

        context = {
            'registrations': regs,
            'search_date': search_date,
            'selected_event': event_id,
            'events': events,
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

from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import registrations
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_POST
def update_print_job_status(request, job_id):
    if request.method == 'POST':
        try:
            job = PrintJob.objects.get(id=job_id)
            data = json.loads(request.body)
            status = data.get('status')
            
            if status in [choice[0] for choice in PrintJob.STATUS_CHOICES]:
                job.status = status
                job.completed_at = timezone.now()
                job.save()
                return JsonResponse({'success': True, 'status': status})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
        except PrintJob.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Job not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@require_POST
def update_registration_status(request, registration_id):
    registration = get_object_or_404(registrations, id=registration_id)
    new_status = request.POST.get('status')

    if new_status in ["Pending", "Approved", "Rejected"]:
        registration.status = new_status
        registration.save()
        messages.success(request, f"Status updated to {new_status}")
    else:
        messages.error(request, "Invalid status selected.")

    return redirect(request.META.get('HTTP_REFERER', 'registrations'))

@login_required
def registration_dashboard(request):
    if not request.user.is_superuser:
        return redirect('login')
    data = registrations.objects.select_related('event__Category').all()
    reg_list = [
        {
            "username": r.username,
            "roll_no": r.roll_no,
            "phone": r.phone,
            "branch": r.branch,
            "utr": r.utr,
            "status": r.status,
            "event": r.event.name,
            "category": r.event.Category.name,  # <<-- Category name from FK
        }
        for r in data
    ]
    count = 0
    reg = registrations.objects.filter(status="Approved")
    for i in reg:
        if i.event.name == "E - Sports":
            if i.participation_mode == "Ludo":
                count += 1
            else:
                count += 4
        else:
            count += 1
            if i.members is not None:
                count += len(i.members)
    return render(request, "dashboard.html", {"registration_data": reg_list,"count":count})

def event_detail(request,event_id):
    return render(request,'index.html',{"event_id":event_id})

@login_required
def event_registrations(request):
    event = Events.objects.get(coordinator=request.user.id)
    regs = registrations.objects.filter(event=event).exclude(status="Rejected")
    intenal = regs.filter(college="MITS").count()
    external = regs.exclude(college="MITS").count()
    total = regs.count()
    print("Internal", intenal)
    print("External", external)
    print("Total", total)
    print("Registrations", regs)
    return render(request, 'event_registrations.html', {'regs': regs, 'Internal': intenal, 'External': external, 'Total': total, 'Event': event})

@login_required
def pending_registration_list(request):
    if request.user.is_superuser:
    # Get the search parameters
        search_date = request.GET.get('search_date')
        print(search_date)
        event_id = request.GET.get('event')  # Get the category from the query parameters
        if search_date == '':
            search_date = None
        # Retrieve all registrations by default
        regs = registrations.objects.filter(status="Pending")

        # Filter registrations by date if provided
        if search_date:
            try:
                date_object = datetime.strptime(search_date, '%Y-%m-%d').date()
                regs = regs.filter(registered_on=date_object)
            except ValueError:
                pass

        # Filter registrations by category if provided
        if event_id:
            regs = regs.filter(event__id=event_id)

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

        # Retrieve all categories for the filter dropdown\
        events = Events.objects.all()

        context = {
            'registrations': regs,
            'search_date': search_date,
            'selected_event': event_id,
            'events': events,
        }
        return render(request, 'registrations.html', context)
    elif request.user.is_authenticated:
        
        event = Events.objects.filter(coordinator=request.user.id).first()
        regs = registrations.objects.filter(event=event)
        return render(request, 'registrations.html', {'registrations': regs})
    else:
        return redirect('login')

@login_required
def rejected_registration_list(request):
    if request.user.is_superuser:
    # Get the search parameters
        search_date = request.GET.get('search_date')
        print(search_date)
        event_id = request.GET.get('event')  # Get the category from the query parameters
        if search_date == '':
            search_date = None
        # Retrieve all registrations by default
        regs = registrations.objects.filter(status="Rejected")

        # Filter registrations by date if provided
        if search_date:
            try:
                date_object = datetime.strptime(search_date, '%Y-%m-%d').date()
                regs = regs.filter(registered_on=date_object)
            except ValueError:
                pass

        # Filter registrations by category if provided
        if event_id:
            regs = regs.filter(event__id=event_id)

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

        # Retrieve all categories for the filter dropdown\
        events = Events.objects.all()

        context = {
            'registrations': regs,
            'search_date': search_date,
            'selected_event': event_id,
            'events': events,
        }
        return render(request, 'registrations.html', context)
    elif request.user.is_authenticated:
        
        event = Events.objects.filter(coordinator=request.user.id).first()
        regs = registrations.objects.filter(event=event)
        return render(request, 'registrations.html', {'registrations': regs})
    else:
        return redirect('login')

@login_required
def approved_registration_list(request):
    if request.user.is_superuser:
    # Get the search parameters
        search_date = request.GET.get('search_date')
        print(search_date)
        event_id = request.GET.get('event')  # Get the category from the query parameters
        if search_date == '':
            search_date = None
        # Retrieve all registrations by default
        regs = registrations.objects.filter(status="Approved")

        # Filter registrations by date if provided
        if search_date:
            try:
                date_object = datetime.strptime(search_date, '%Y-%m-%d').date()
                regs = regs.filter(registered_on=date_object)
            except ValueError:
                pass

        # Filter registrations by category if provided
        if event_id:
            regs = regs.filter(event__id=event_id)

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

        # Retrieve all categories for the filter dropdown\
        events = Events.objects.all()

        context = {
            'registrations': regs,
            'search_date': search_date,
            'selected_event': event_id,
            'events': events,
        }
        return render(request, 'registrations.html', context)
    elif request.user.is_authenticated:
        
        event = Events.objects.filter(coordinator=request.user.id).first()
        regs = registrations.objects.filter(event=event)
        return render(request, 'registrations.html', {'registrations': regs})
    else:
        return redirect('login')

@login_required
def total_amount_view(request):
    if request.user.is_superuser:
        regs = registrations.objects.filter(status="Approved")
        total_amount = 0
        event_totals = {}

        for reg in regs:
            team_size = len(reg.members) + 1 if reg.members else 1
            is_internal = reg.college.strip() == "MITS"
            
            if reg.event.name == "E - Sports":
                if reg.participation_mode == "Ludo":
                    amount = 50 if is_internal else 100
                else:
                    amount = 100 if is_internal else 200
            else:
                amount = team_size * (50 if is_internal else 100)
            
            total_amount += amount
            
            # Track totals by event
            event_name = reg.event.name
            if event_name not in event_totals:
                event_totals[event_name] = {
                    'total': 0,
                    'internal_count': 0,
                    'external_count': 0,
                    'internal_amount': 0,
                    'external_amount': 0
                }
            
            event_totals[event_name]['total'] += amount
            if is_internal:
                event_totals[event_name]['internal_count'] += 1
                event_totals[event_name]['internal_amount'] += amount
            else:
                event_totals[event_name]['external_count'] += 1
                event_totals[event_name]['external_amount'] += amount

        context = {
            'total_amount': total_amount,
            'event_totals': event_totals,
        }
        return render(request, 'amount_details.html', context)
    else:
        return HttpResponse("Unauthorised Access")

@login_required
def upload_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        copies = request.POST.get('copies', 1)
        orientation = request.POST.get('orientation', 'portrait')
        pages_per_sheet = request.POST.get('pages_per_sheet', 1)

        if file:
            PrintJob.objects.create(
                user=request.user,
                file=file,
                copies=copies,
                orientation=orientation,
                pages_per_sheet=pages_per_sheet
            )
            messages.success(request, 'File uploaded successfully!')
            return redirect('print_jobs')
        
    return render(request, 'print/upload.html')

@login_required
def print_jobs(request):
    if request.user.is_superuser:
        jobs = PrintJob.objects.filter(status='pending')
    else:
        jobs = PrintJob.objects.filter(user=request.user)
    return render(request, 'print/jobs.html', {'jobs': jobs})

def print_file(file_path, copies, orientation, pages_per_sheet):
    try:
        # Initialize CUPS connection
        conn = cups.Connection()
        printers = conn.getPrinters()
        if not printers:
            return False, "No printers found"
        
        # Get the default printer
        default_printer = conn.getDefault()
        if not default_printer:
            # If no default printer is set, use the first available printer
            default_printer = list(printers.keys())[0]
        
        # Set printing options
        options = {
            'copies': str(copies),
            'orientation-requested': '3' if orientation == 'portrait' else '4',  # 3 for portrait, 4 for landscape
            'number-up': str(pages_per_sheet),
            'fit-to-page': 'True',
            'media': 'A4',  # Set default paper size to A4
        }
        
        # Add additional printer-specific options based on file type
        file_ext = file_path.lower().split('.')[-1]
        if file_ext in ['pdf', 'PDF']:
            options.update({
                'page-set': 'all',
                'collate': 'True'
            })
        
        # Send print job to printer
        job_id = conn.printFile(default_printer, file_path, f"Print Job - {file_path.split('/')[-1]}", options)
        
        # Wait for job to complete and check status
        import time
        max_wait = 30  # Maximum wait time in seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            jobs = conn.getJobs()
            if job_id not in jobs:
                # Job completed successfully
                return True, job_id
            if jobs[job_id]['state'] in ['aborted', 'canceled', 'failed']:
                return False, f"Print job failed with status: {jobs[job_id]['state']}"
            time.sleep(1)
            
        return False, "Print job timed out"
    except cups.IPPError as ipp_error:
        return False, f"CUPS printing error: {ipp_error}"
    except Exception as e:
        return False, f"Printing error: {str(e)}"

@login_required
def print_all(request):
    if not request.user.is_superuser:
        messages.error(request, 'Unauthorized access')
        return redirect('print_jobs')
    
    if request.method == 'POST':
        pending_jobs = PrintJob.objects.filter(status='pending')
        current_time = timezone.now()
        
        for job in pending_jobs:
            job.status = 'completed'
            job.completed_at = current_time
            job.save()
        
        messages.success(request, f'{pending_jobs.count()} jobs marked as completed')
    
    return redirect('print_jobs')

@login_required
def completed_print_jobs(request):
    """View to display completed print jobs"""
    if request.user.is_superuser:
        jobs = PrintJob.objects.filter(status='completed').order_by('-completed_at')
    else:
        jobs = PrintJob.objects.filter(user=request.user, status='completed').order_by('-completed_at')
    return render(request, 'print/completed_jobs.html', {'jobs': jobs})

