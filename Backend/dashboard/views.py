import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from db import customers_collection, drivers_collection, bookings_collection, payments_collection

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body) if request.body else {}
            role = data.get("role", "").strip().lower()
            email = data.get("email", "").strip()
            password = data.get("password", "").strip()

            if not role:
                return JsonResponse({"error": "Role is required"}, status=400)

            if role == "admin":
                if email == "admin" and password == "admin123":
                    return JsonResponse({
                        "message": "Admin login successful",
                        "user": {
                            "role": "admin",
                            "name": "Administrator",
                            "email": "admin@taxi.com"
                        }
                    })
                return JsonResponse({"error": "Invalid Admin credentials"}, status=401)

            elif role == "customer":
                if not email or not password:
                    return JsonResponse({"error": "Email and Password are required"}, status=400)
                customer = customers_collection.find_one({"email": email})
                if customer and customer.get("password") == password:
                    return JsonResponse({
                        "message": "Customer login successful",
                        "user": {
                            "role": "customer",
                            "id": customer.get("customer_id"),
                            "name": customer.get("full_name"),
                            "email": customer.get("email")
                        }
                    })
                return JsonResponse({"error": "Invalid Customer credentials"}, status=401)

            elif role == "driver":
                if not email or not password:
                    return JsonResponse({"error": "Email and License/Phone are required"}, status=400)
                # For drivers, since there is no password in driver schema,
                # we authenticate by matching email and phone/license_number.
                driver = drivers_collection.find_one({"email": email})
                if driver and (driver.get("license_number") == password or driver.get("phone") == password):
                    return JsonResponse({
                        "message": "Driver login successful",
                        "user": {
                            "role": "driver",
                            "id": driver.get("driver_id"),
                            "name": driver.get("driver_name"),
                            "email": driver.get("email"),
                            "license_number": driver.get("license_number")
                        }
                    })
                return JsonResponse({"error": "Invalid Driver credentials. Use email and License/Phone as password."}, status=401)

            else:
                return JsonResponse({"error": "Invalid role specified"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)


def get_dashboard_stats(request):
    """
    Get dashboard statistics for a quick admin or dashboard load
    """
    if request.method == "GET":
        try:
            total_customers = customers_collection.count_documents({})
            total_drivers = drivers_collection.count_documents({})
            total_bookings = bookings_collection.count_documents({})
            
            # Sum of completed payments
            payments = payments_collection.find({"payment_status": "Success"})
            total_earnings = sum(float(p.get("amount", 0)) for p in payments)

            # Count of rides by status
            bookings = bookings_collection.find({})
            completed_rides = sum(1 for b in bookings if b.get("ride_status") == "Completed")
            active_rides = sum(1 for b in bookings if b.get("ride_status") in ["Accepted", "In Progress"])
            pending_rides = sum(1 for b in bookings if b.get("ride_status") == "Requested")

            stats = {
                "total_customers": total_customers,
                "total_drivers": total_drivers,
                "total_bookings": total_bookings,
                "total_earnings": total_earnings,
                "completed_rides": completed_rides,
                "active_rides": active_rides,
                "pending_rides": pending_rides
            }
            return JsonResponse(stats)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)
