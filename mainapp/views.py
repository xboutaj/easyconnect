from django.shortcuts import render, redirect
from mainapp.decorators import role_required
from core.mqtt_client import latest_message
from django.http import JsonResponse
from .models import Event, Ticket, EmployeeProfile, Device
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json


def home(request):
    return render(request, 'main/index.html')

@role_required('admin')
def admin(request):
    return render(request, 'main/admin.html')

@role_required('vendor')
def vendor(request):
    return render(request, 'main/vendor.html')

@role_required('attendee')
def attendee(request):
    return render(request, 'main/attendee.html')

def ticket_dashboard(request):
    msg = latest_message.get("easyconnect/ticket", "No ticket data")
    return render(request, "mainapp/dashboard.html", {"ticket_info": msg})


def attendee_dashboard(request):
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, "main/attendee.html", {"tickets": tickets})

def get_events_json(request):
    events = Event.objects.all().values("id", "title", "location", "date", "time")
    return JsonResponse(list(events), safe=False)


@login_required
def employee_dashboard(request):
    return render(request, 'main/employee.html')

@csrf_exempt
def join_event_employee(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        event_code = data.get('event_code')
        try:
            event = Event.objects.get(employee_code=event_code)
            # Assign event to employee user profile if needed
            return JsonResponse({'success': True, 'event_id': event.id})
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid event code'})

@csrf_exempt
def scan_ticket_qr(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ticket_id = data.get('ticket_id')
        try:
            ticket = Ticket.objects.get(ticket_id=ticket_id)
            device = Device.objects.filter(available=True).first()
            if device:
                device.assigned_ticket = ticket
                device.available = False
                device.save()
                return JsonResponse({'success': True, 'device_id': device.device_id})
            else:
                return JsonResponse({'success': False, 'error': 'No available devices'})
        except Ticket.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Ticket not found'})


@login_required
def scanner_view(request):
    return render(request, 'main/scanner.html')

@csrf_exempt
def assign_device_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ticket_id = data.get('ticket_id')

        # Simulate device assignment logic
        device = Device.objects.filter(available=True).first()
        if device:
            device.assigned_ticket = ticket_id
            device.available = False
            device.save()
            return JsonResponse({'success': True, 'message': f'Device {device.device_id} assigned.'})
        else:
            return JsonResponse({'success': False, 'message': 'No available devices.'})





