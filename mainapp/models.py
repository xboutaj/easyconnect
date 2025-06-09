from django.db import models
from django.contrib.auth import get_user_model
import uuid

# Extended Profile for any user role (attendee, admin, vendor)
class UserProfile(models.Model):
    
    ROLE_CHOICES = [
        ('attendee', 'Attendee'),
        ('vendor', 'Vendor'),
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    ]

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True)
    linkedin = models.URLField(blank=True)
    website = models.URLField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    dob = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

# Event model created by host/admin
class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    host = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='hosted_events')
    attendee_code = models.CharField(max_length=10, unique=True)
    employee_code = models.CharField(max_length=10, unique=True)
    vendor_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} on {self.date}"

# Ticket associated with users after joining an event
# class Ticket(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     event = models.ForeignKey(Event, on_delete=models.CASCADE)
#     ticket_id = models.CharField(max_length=36, default=uuid.uuid4, unique=True)
#     tier = models.CharField(max_length=20, default='General')

#     def __str__(self):
#         return f"{self.ticket_id} for {self.user.username}"

class Ticket(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    ticket_id = models.CharField(max_length=100, unique=True)
    event_name = models.CharField(max_length=200)
    event_date = models.DateTimeField()
    ticket_type = models.CharField(max_length=50, choices=[
        ('GA', 'General Admission'),
        ('VIP', 'VIP'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticket_id} ({self.event_name})"
    

# Vendor information for vendors
class VendorInfo(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    goal = models.TextField(blank=True)
    reps = models.TextField(blank=True)

    def __str__(self):
        return f"{self.organization_name} at {self.event.name}"

# Connection between two ticket holders (recorded after handshake)
class Connection(models.Model):
    ticket_1 = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='initiated_connections')
    ticket_2 = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='received_connections')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticket_1.ticket_id} ↔ {self.ticket_2.ticket_id}"

# Devices that are available for assigning to attendees 
# class Device(models.Model):
#     device_id = models.CharField(max_length=50, unique=True)
#     is_available = models.BooleanField(default=True)
#     assigned_ticket = models.OneToOneField(Ticket, on_delete=models.SET_NULL, null=True, blank=True)
#     assigned_event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)

#     def __str__(self):
#         return f"Device {self.device_id} ({'Available' if self.is_available else 'Assigned'})"
    
class Device(models.Model):
    device_id = models.CharField(max_length=100, unique=True)
    assigned_ticket = models.CharField(max_length=100, blank=True, null=True)
    available = models.BooleanField(default=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = "Available" if self.available else f"Assigned to {self.assigned_ticket}"
        return f"Device {self.device_id} - {status}"
    

# Employee account 
class EmployeeProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    joined_events = models.ManyToManyField(Event, related_name="employees")
    phone_number = models.CharField(max_length=20, blank=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Employee: {self.user.username}"
