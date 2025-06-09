from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin-panel/', views.admin, name='admin'),
    path('vendor-panel/', views.vendor, name='vendor'),
    path('attendee-panel/', views.attendee, name='attendee'),
    path('dashboard/', views.attendee_dashboard, name='attendee_dashboard'),
    path('create-event/', views.create_event, name='create_event'),
    path('api/events/', views.get_events_json, name='get_events_json'),
    path('dashboard/employee/', views.employee_dashboard, name='employee_dashboard'),
    # path('employee/join_event/', views.join_event_as_employee, name='join_event_as_employee'),
    # path('employee/scan_qr/', views.scan_qr, name='scan_qr'),  # This will simulate QR scanning logic
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employee/scan/', views.scanner_view, name='scanner_view'),
    path('api/assign-device/', views.assign_device_api, name='assign_device_api'),
    path('join-employee-event/', views.join_event_employee, name='join_event_employee'),
    path('join-event/', views.join_event, name='join_event'),
    path('scan-ticket/', views.scan_ticket_qr, name='scan_ticket'),
]
