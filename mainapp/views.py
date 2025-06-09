from django.shortcuts import render, redirect, get_object_or_404
from mainapp.decorators import role_required
from core.mqtt_client import latest_message, publish_message
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
import uuid
import random
import string
from datetime import datetime
from .models import Event, Ticket, EmployeeProfile, Device, UserProfile, Connection
from django.db import models
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json


def home(request):
    return render(request, 'main/index.html')

@role_required('admin')
def admin(request):
    today = timezone.now().date()
    events = Event.objects.filter(host=request.user).order_by('date')
    context = {
        'upcoming_events': events.filter(date__gte=today),
        'past_events': events.filter(date__lt=today)
    }
    return render(request, 'main/admin.html', context)

@login_required
@role_required('attendee')
def attendee(request):
    return attendee_dashboard(request)

def ticket_dashboard(request):
    msg = latest_message.get("easyconnect/ticket", "No ticket data")
    return render(request, "mainapp/dashboard.html", {"ticket_info": msg})


@login_required
@role_required('attendee')
def attendee_dashboard(request):
    tickets = Ticket.objects.filter(user=request.user).order_by('event_date')
    now = timezone.now()
    context = {
        'upcoming_events': tickets.filter(event_date__gte=now),
        'past_events': tickets.filter(event_date__lt=now)
    }
    return render(request, "main/attendee.html", context)


@login_required
@role_required('attendee')
def attendee_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'attendee'})
    if request.method == 'POST':
        request.user.full_name = request.POST.get('full_name', request.user.full_name)
        request.user.save()

        profile.bio = request.POST.get('bio', profile.bio)
        profile.linkedin = request.POST.get('linkedin', profile.linkedin)
        profile.website = request.POST.get('website', profile.website)
        if request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES['profile_picture']
        profile.save()

        messages.success(request, 'Profile updated successfully')
        return redirect('attendee_profile')

    context = {'profile': profile}
    return render(request, 'main/profile.html', context)

@login_required
@role_required('admin')
def create_event(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        date = request.POST.get('date')
        time_val = request.POST.get('time')
        location = request.POST.get('location')

        def gen_code():
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        event = Event.objects.create(
            name=name,
            description=description,
            date=date,
            time=time_val,
            location=location,
            host=request.user,
            attendee_code=gen_code(),
            employee_code=gen_code(),
        )
        messages.success(request, 'Event created successfully')
        return redirect('admin')
    return render(request, 'main/create_event.html')

def get_events_json(request):
    events = Event.objects.all().values("id", "name", "location", "date", "time")
    return JsonResponse(list(events), safe=False)


@login_required
@csrf_exempt
def join_event(request):
    if request.method == 'POST':
        event_code = request.POST.get('event_code')
        try:
            event = Event.objects.get(attendee_code=event_code)
        except Event.DoesNotExist:
            messages.error(request, 'Invalid event code')
            return redirect('attendee_dashboard')

        event_dt = timezone.make_aware(datetime.combine(event.date, event.time))
        Ticket.objects.get_or_create(
            user=request.user,
            event_name=event.name,
            event_date=event_dt,
            defaults={'ticket_id': uuid.uuid4().hex, 'ticket_type': 'GA'}
        )
        messages.success(request, 'Event joined successfully')
        return redirect('attendee_dashboard')
    return redirect('attendee_dashboard')


@login_required
@role_required('employee')
def employee(request):
    profile, _ = EmployeeProfile.objects.get_or_create(user=request.user)
    events = profile.joined_events.all().order_by('date')
    today = timezone.now().date()
    context = {
        'upcoming_events': events.filter(date__gte=today),
        'past_events': events.filter(date__lt=today)
    }
    return render(request, 'main/employee.html', context)

@csrf_exempt
def join_event_employee(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            event_code = data.get('event_code')
        else:
            event_code = request.POST.get('event_code')
        try:
            event = Event.objects.get(employee_code=event_code)
            profile, _ = EmployeeProfile.objects.get_or_create(user=request.user)
            profile.joined_events.add(event)
            if request.content_type == 'application/json':
                return JsonResponse({'success': True, 'event_id': event.id})
            messages.success(request, 'Event joined successfully')
            return redirect('employee')
        except Event.DoesNotExist:
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'error': 'Invalid event code'})
            messages.error(request, 'Invalid event code')
            return redirect('employee')

@csrf_exempt
def scan_ticket_qr(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ticket_id = data.get('ticket_id')
        try:
            Ticket.objects.get(ticket_id=ticket_id)
            device = Device.objects.filter(available=True).first()
            if device:
                device.assigned_ticket = ticket_id
                device.available = False
                device.save()
                publish_message(
                    f"device/{device.device_id}/control",
                    json.dumps({"ticket_id": ticket_id})
                )
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
            publish_message(
                f"device/{device.device_id}/control",
                json.dumps({"ticket_id": ticket_id})
            )
            return JsonResponse({'success': True, 'message': f'Device {device.device_id} assigned.'})
        else:
            return JsonResponse({'success': False, 'message': 'No available devices.'})





@login_required
@role_required('attendee')
def event_connections(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id, user=request.user)
    event = get_object_or_404(Event, name=ticket.event_name, date=ticket.event_date.date())
    connections_qs = Connection.objects.filter(event=event)
    connections_qs = connections_qs.filter(models.Q(ticket_1=ticket) | models.Q(ticket_2=ticket)).select_related('ticket_1__user', 'ticket_2__user')
    connections = []
    for conn in connections_qs:
        if conn.ticket_1 == ticket:
            connections.append(conn.ticket_2)
        else:
            connections.append(conn.ticket_1)
    context = {'ticket': ticket, 'connections': connections}
    return render(request, 'main/event_connections.html', context)


