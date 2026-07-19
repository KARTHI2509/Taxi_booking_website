import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from db import customers_collection

# GET: List customers (or search by name/phone/email)
def get_customers(request):
    if request.method == "GET":
        try:
            search_query = request.GET.get("search", "").strip()
            query = {}
            if search_query:
                query = {
                    "$or": [
                        {"full_name": {"$regex": search_query, "$options": "i"}},
                        {"phone": {"$regex": search_query, "$options": "i"}},
                        {"email": {"$regex": search_query, "$options": "i"}}
                    ]
                }
            customers = list(customers_collection.find(query, {"_id": 0}))
            return JsonResponse(customers, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

# POST: Add customer
@csrf_exempt
def add_customer(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body) if request.body else {}
            full_name = data.get("full_name", "").strip()
            email = data.get("email", "").strip()
            password = data.get("password", "").strip()

            if not full_name:
                return JsonResponse({"error": "Full name is required"}, status=400)
            if not email:
                return JsonResponse({"error": "Email is required"}, status=400)
            if not password:
                return JsonResponse({"error": "Password is required"}, status=400)

            # Check if email already exists
            existing_email = customers_collection.find_one({"email": email})
            if existing_email:
                return JsonResponse({"error": f"Customer with email {email} already exists"}, status=400)

            # Auto-increment ID starting at 101
            customer_id = data.get("customer_id")
            if not customer_id:
                max_doc = customers_collection.find_one(sort=[("customer_id", -1)])
                customer_id = (max_doc["customer_id"] + 1) if max_doc and "customer_id" in max_doc else 101
            else:
                customer_id = int(customer_id)

            if customers_collection.find_one({"customer_id": customer_id}):
                return JsonResponse({"error": f"Customer ID {customer_id} already exists"}, status=400)

            customer_doc = {
                "customer_id": customer_id,
                "full_name": full_name,
                "email": email,
                "phone": data.get("phone", "").strip(),
                "address": data.get("address", "").strip(),
                "password": password
            }

            customers_collection.insert_one(customer_doc)
            return JsonResponse({"message": "Customer added successfully", "customer_id": customer_id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

# PUT: Update customer
@csrf_exempt
def update_customer(request, id):
    if request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else {}
            data.pop("customer_id", None)  # Prevent changing ID

            result = customers_collection.update_one(
                {"customer_id": int(id)},
                {"$set": data}
            )

            if result.matched_count > 0:
                return JsonResponse({"message": "Customer updated successfully"})
            return JsonResponse({"error": "Customer not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

# DELETE: Delete customer
@csrf_exempt
def delete_customer(request, id):
    if request.method == "DELETE":
        try:
            result = customers_collection.delete_one({"customer_id": int(id)})
            if result.deleted_count > 0:
                return JsonResponse({"message": "Customer deleted successfully"})
            return JsonResponse({"error": "Customer not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)
