import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from db import bookings_collection

# GET: List bookings (supports filtering by customer_name, driver_name, or ride_status)
def get_bookings(request):
    if request.method == "GET":
        try:
            customer_name = request.GET.get("customer_name", "").strip()
            driver_name = request.GET.get("driver_name", "").strip()
            ride_status = request.GET.get("ride_status", "").strip()
            search_query = request.GET.get("search", "").strip()

            query = {}
            if customer_name:
                query["customer_name"] = customer_name
            if driver_name:
                query["driver_name"] = driver_name
            if ride_status:
                query["ride_status"] = ride_status

            if search_query:
                query["$or"] = [
                    {"customer_name": {"$regex": search_query, "$options": "i"}},
                    {"driver_name": {"$regex": search_query, "$options": "i"}},
                    {"pickup_location": {"$regex": search_query, "$options": "i"}},
                    {"drop_location": {"$regex": search_query, "$options": "i"}}
                ]

            bookings = list(bookings_collection.find(query, {"_id": 0}))
            
            # Sort by booking_id descending to show recent rides first
            bookings.sort(key=lambda x: x.get("booking_id", 0), reverse=True)
            return JsonResponse(bookings, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

# POST: Add booking
@csrf_exempt
def add_booking(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body) if request.body else {}
            customer_name = data.get("customer_name", "").strip()
            pickup_location = data.get("pickup_location", "").strip()
            drop_location = data.get("drop_location", "").strip()
            booking_date = data.get("booking_date", "").strip()

            if not customer_name:
                return JsonResponse({"error": "Customer name is required"}, status=400)
            if not pickup_location:
                return JsonResponse({"error": "Pickup location is required"}, status=400)
            if not drop_location:
                return JsonResponse({"error": "Drop location is required"}, status=400)
            if not booking_date:
                return JsonResponse({"error": "Booking date is required"}, status=400)

            # Auto-increment ID starting at 401
            booking_id = data.get("booking_id")
            if not booking_id:
                max_doc = bookings_collection.find_one(sort=[("booking_id", -1)])
                booking_id = (max_doc["booking_id"] + 1) if max_doc and "booking_id" in max_doc else 401
            else:
                booking_id = int(booking_id)

            if bookings_collection.find_one({"booking_id": booking_id}):
                return JsonResponse({"error": f"Booking ID {booking_id} already exists"}, status=400)

            booking_doc = {
                "booking_id": booking_id,
                "customer_name": customer_name,
                "driver_name": data.get("driver_name", "Pending").strip(),
                "pickup_location": pickup_location,
                "drop_location": drop_location,
                "booking_date": booking_date,
                "fare": float(data.get("fare", 0.0)),
                "ride_status": data.get("ride_status", "Requested").strip()
            }

            bookings_collection.insert_one(booking_doc)
            return JsonResponse({"message": "Booking created successfully", "booking_id": booking_id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

# PUT: Update booking
@csrf_exempt
def update_booking(request, id):
    if request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else {}
            data.pop("booking_id", None)  # Prevent changing ID

            if "fare" in data:
                data["fare"] = float(data["fare"])

            result = bookings_collection.update_one(
                {"booking_id": int(id)},
                {"$set": data}
            )

            if result.matched_count > 0:
                return JsonResponse({"message": "Booking updated successfully"})
            return JsonResponse({"error": "Booking not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

# DELETE: Delete booking
@csrf_exempt
def delete_booking(request, id):
    if request.method == "DELETE":
        try:
            result = bookings_collection.delete_one({"booking_id": int(id)})
            if result.deleted_count > 0:
                return JsonResponse({"message": "Booking deleted successfully"})
            return JsonResponse({"error": "Booking not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)
