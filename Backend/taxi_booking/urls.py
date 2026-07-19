import os
import mimetypes
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.http import HttpResponse, Http404

# Import views from individual apps
from customers import views as customer_views
from drivers import views as driver_views
from vehicles import views as vehicle_views
from bookings import views as booking_views
from payments import views as payment_views
from dashboard import views as dashboard_views

def serve_frontend_file(request, filename="index.html"):
    if not filename:
        filename = "index.html"
    # Serve static assets or HTML files from the Frontend folder
    file_path = os.path.join(settings.BASE_DIR.parent, "Frontend", filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        content_type, _ = mimetypes.guess_type(file_path)
        # Fallback MIME types for development
        if filename.endswith(".css"):
            content_type = "text/css"
        elif filename.endswith(".js"):
            content_type = "application/javascript"
        
        with open(file_path, "rb") as f:
            return HttpResponse(f.read(), content_type=content_type)
    raise Http404(f"File {filename} not found at {file_path}")

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication & Dashboard APIs
    path('api/login/', dashboard_views.login_view, name='login_api'),
    path('api/stats/', dashboard_views.get_dashboard_stats, name='stats_api'),

    # Customers API
    path('customers/', customer_views.get_customers, name='get_customers'),
    path('customers/add/', customer_views.add_customer, name='add_customer'),
    path('customers/update/<int:id>/', customer_views.update_customer, name='update_customer'),
    path('customers/delete/<int:id>/', customer_views.delete_customer, name='delete_customer'),

    # Drivers API
    path('drivers/', driver_views.get_drivers, name='get_drivers'),
    path('drivers/add/', driver_views.add_driver, name='add_driver'),
    path('drivers/update/<int:id>/', driver_views.update_driver, name='update_driver'),
    path('drivers/delete/<int:id>/', driver_views.delete_driver, name='delete_driver'),

    # Vehicles API
    path('vehicles/', vehicle_views.get_vehicles, name='get_vehicles'),
    path('vehicles/add/', vehicle_views.add_vehicle, name='add_vehicle'),
    path('vehicles/update/<int:id>/', vehicle_views.update_vehicle, name='update_vehicle'),
    path('vehicles/delete/<int:id>/', vehicle_views.delete_vehicle, name='delete_vehicle'),

    # Bookings API
    path('bookings/', booking_views.get_bookings, name='get_bookings'),
    path('bookings/add/', booking_views.add_booking, name='add_booking'),
    path('bookings/update/<int:id>/', booking_views.update_booking, name='update_booking'),
    path('bookings/delete/<int:id>/', booking_views.delete_booking, name='delete_booking'),

    # Payments API
    path('payments/', payment_views.get_payments, name='get_payments'),
    path('payments/add/', payment_views.add_payment, name='add_payment'),
    path('payments/update/<int:id>/', payment_views.update_payment, name='update_payment'),
    path('payments/delete/<int:id>/', payment_views.delete_payment, name='delete_payment'),

    # Frontend routes
    path('', serve_frontend_file, {"filename": "index.html"}),
    path('<str:filename>', serve_frontend_file),
]
