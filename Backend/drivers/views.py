import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from db import drivers_collection

# GET: List drivers (or search by name/license/email)
def get_drivers(request):
    if request.method == "GET":
        try:
            search_query = request.GET.get("search", "").strip()
            query = {}
            if search_query:
                query = {
                    "$or": [
                        {"driver_name": {"$regex": search_query, "$options": "i"}},
                        {"license_number": {"$regex": search_query, "$options": "i"}},
                        {"email": {"$regex": search_query, "$options": "i"}}
                    ]
                }
            drivers = list(drivers_collection.find(query, {"_id": 0}))
            return JsonResponse(drivers, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

# POST: Add driver
@csrf_exempt
def add_driver(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body) if request.body else {}
            driver_name = data.get("driver_name", "").strip()
            email = data.get("email", "").strip()
            license_number = data.get("license_number", "").strip()

            if not driver_name:
                return JsonResponse({"error": "Driver name is required"}, status=400)
            if not email:
                return JsonResponse({"error": "Email is required"}, status=400)
            if not license_number:
                return JsonResponse({"error": "License number is required"}, status=400)

            # Check if email or license number exists
            if drivers_collection.find_one({"email": email}):
                return JsonResponse({"error": f"Driver with email {email} already exists"}, status=400)
            if drivers_collection.find_one({"license_number": license_number}):
                return JsonResponse({"error": f"License number {license_number} already exists"}, status=400)

            # Auto-increment ID starting at 201
            driver_id = data.get("driver_id")
            if not driver_id:
                max_doc = drivers_collection.find_one(sort=[("driver_id", -1)])
                driver_id = (max_doc["driver_id"] + 1) if max_doc and "driver_id" in max_doc else 201
            else:
                driver_id = int(driver_id)

            if drivers_collection.find_one({"driver_id": driver_id}):
                return JsonResponse({"error": f"Driver ID {driver_id} already exists"}, status=400)

            driver_doc = {
                "driver_id": driver_id,
                "driver_name": driver_name,
                "email": email,
                "phone": data.get("phone", "").strip(),
                "license_number": license_number,
                "experience": int(data.get("experience", 0)),
                "availability": data.get("availability", "Available").strip()
            }

            drivers_collection.insert_one(driver_doc)
            return JsonResponse({"message": "Driver added successfully", "driver_id": driver_id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

# PUT: Update driver
@csrf_exempt
def update_driver(request, id):
    if request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else {}
            data.pop("driver_id", None)  # Prevent changing ID

            if "experience" in data:
                data["experience"] = int(data["experience"])

            result = drivers_collection.update_one(
                {"driver_id": int(id)},
                {"$set": data}
            )

            if result.matched_count > 0:
                return JsonResponse({"message": "Driver updated successfully"})
            return JsonResponse({"error": "Driver not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

# DELETE: Delete driver
@csrf_exempt
def delete_driver(request, id):
    if request.method == "DELETE":
        try:
            result = drivers_collection.delete_one({"driver_id": int(id)})
            if result.deleted_count > 0:
                return JsonResponse({"message": "Driver deleted successfully"})
            return JsonResponse({"error": "Driver not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)
