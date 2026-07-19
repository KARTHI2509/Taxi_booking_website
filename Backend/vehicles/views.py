import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from db import vehicles_collection

# GET: List vehicles (or search by model/number/driver_name)
def get_vehicles(request):
    if request.method == "GET":
        try:
            search_query = request.GET.get("search", "").strip()
            query = {}
            if search_query:
                query = {
                    "$or": [
                        {"model": {"$regex": search_query, "$options": "i"}},
                        {"vehicle_number": {"$regex": search_query, "$options": "i"}},
                        {"driver_name": {"$regex": search_query, "$options": "i"}},
                        {"vehicle_type": {"$regex": search_query, "$options": "i"}}
                    ]
                }
            vehicles = list(vehicles_collection.find(query, {"_id": 0}))
            return JsonResponse(vehicles, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

# POST: Add vehicle
@csrf_exempt
def add_vehicle(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body) if request.body else {}
            driver_name = data.get("driver_name", "").strip()
            vehicle_type = data.get("vehicle_type", "").strip()
            vehicle_number = data.get("vehicle_number", "").strip()

            if not driver_name:
                return JsonResponse({"error": "Driver name is required"}, status=400)
            if not vehicle_type:
                return JsonResponse({"error": "Vehicle type is required"}, status=400)
            if not vehicle_number:
                return JsonResponse({"error": "Vehicle number is required"}, status=400)

            # Check if vehicle number already exists
            if vehicles_collection.find_one({"vehicle_number": vehicle_number}):
                return JsonResponse({"error": f"Vehicle number {vehicle_number} already exists"}, status=400)

            # Auto-increment ID starting at 301
            vehicle_id = data.get("vehicle_id")
            if not vehicle_id:
                max_doc = vehicles_collection.find_one(sort=[("vehicle_id", -1)])
                vehicle_id = (max_doc["vehicle_id"] + 1) if max_doc and "vehicle_id" in max_doc else 301
            else:
                vehicle_id = int(vehicle_id)

            if vehicles_collection.find_one({"vehicle_id": vehicle_id}):
                return JsonResponse({"error": f"Vehicle ID {vehicle_id} already exists"}, status=400)

            vehicle_doc = {
                "vehicle_id": vehicle_id,
                "driver_name": driver_name,
                "vehicle_type": vehicle_type,
                "vehicle_number": vehicle_number,
                "seating_capacity": int(data.get("seating_capacity", 4)),
                "model": data.get("model", "").strip()
            }

            vehicles_collection.insert_one(vehicle_doc)
            return JsonResponse({"message": "Vehicle added successfully", "vehicle_id": vehicle_id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

# PUT: Update vehicle
@csrf_exempt
def update_vehicle(request, id):
    if request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else {}
            data.pop("vehicle_id", None)  # Prevent changing ID

            if "seating_capacity" in data:
                data["seating_capacity"] = int(data["seating_capacity"])

            result = vehicles_collection.update_one(
                {"vehicle_id": int(id)},
                {"$set": data}
            )

            if result.matched_count > 0:
                return JsonResponse({"message": "Vehicle updated successfully"})
            return JsonResponse({"error": "Vehicle not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

# DELETE: Delete vehicle
@csrf_exempt
def delete_vehicle(request, id):
    if request.method == "DELETE":
        try:
            result = vehicles_collection.delete_one({"vehicle_id": int(id)})
            if result.deleted_count > 0:
                return JsonResponse({"message": "Vehicle deleted successfully"})
            return JsonResponse({"error": "Vehicle not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)
