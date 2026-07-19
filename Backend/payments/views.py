import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from db import payments_collection

# GET: List payments (supports filtering by customer_name, booking_id)
def get_payments(request):
    if request.method == "GET":
        try:
            customer_name = request.GET.get("customer_name", "").strip()
            booking_id = request.GET.get("booking_id", "").strip()
            search_query = request.GET.get("search", "").strip()

            query = {}
            if customer_name:
                query["customer_name"] = customer_name
            if booking_id:
                query["booking_id"] = int(booking_id)

            if search_query:
                query["$or"] = [
                    {"customer_name": {"$regex": search_query, "$options": "i"}},
                    {"transaction_id": {"$regex": search_query, "$options": "i"}},
                    {"payment_method": {"$regex": search_query, "$options": "i"}}
                ]

            payments = list(payments_collection.find(query, {"_id": 0}))
            
            # Sort by payment_id descending
            payments.sort(key=lambda x: x.get("payment_id", 0), reverse=True)
            return JsonResponse(payments, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

# POST: Add payment
@csrf_exempt
def add_payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body) if request.body else {}
            booking_id = data.get("booking_id")
            customer_name = data.get("customer_name", "").strip()
            amount = data.get("amount")
            payment_method = data.get("payment_method", "").strip()

            if not booking_id:
                return JsonResponse({"error": "Booking ID is required"}, status=400)
            if not customer_name:
                return JsonResponse({"error": "Customer name is required"}, status=400)
            if amount is None:
                return JsonResponse({"error": "Amount is required"}, status=400)
            if not payment_method:
                return JsonResponse({"error": "Payment method is required"}, status=400)

            # Auto-increment ID starting at 501
            payment_id = data.get("payment_id")
            if not payment_id:
                max_doc = payments_collection.find_one(sort=[("payment_id", -1)])
                payment_id = (max_doc["payment_id"] + 1) if max_doc and "payment_id" in max_doc else 501
            else:
                payment_id = int(payment_id)

            if payments_collection.find_one({"payment_id": payment_id}):
                return JsonResponse({"error": f"Payment ID {payment_id} already exists"}, status=400)

            payment_doc = {
                "payment_id": payment_id,
                "booking_id": int(booking_id),
                "customer_name": customer_name,
                "amount": float(amount),
                "payment_method": payment_method,
                "payment_status": data.get("payment_status", "Pending").strip(),
                "transaction_id": data.get("transaction_id", "").strip(),
                "payment_date": data.get("payment_date", "").strip()
            }

            payments_collection.insert_one(payment_doc)
            return JsonResponse({"message": "Payment recorded successfully", "payment_id": payment_id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

# PUT: Update payment
@csrf_exempt
def update_payment(request, id):
    if request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else {}
            data.pop("payment_id", None)  # Prevent changing ID

            if "amount" in data:
                data["amount"] = float(data["amount"])
            if "booking_id" in data:
                data["booking_id"] = int(data["booking_id"])

            result = payments_collection.update_one(
                {"payment_id": int(id)},
                {"$set": data}
            )

            if result.matched_count > 0:
                return JsonResponse({"message": "Payment updated successfully"})
            return JsonResponse({"error": "Payment not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

# DELETE: Delete payment
@csrf_exempt
def delete_payment(request, id):
    if request.method == "DELETE":
        try:
            result = payments_collection.delete_one({"payment_id": int(id)})
            if result.deleted_count > 0:
                return JsonResponse({"message": "Payment deleted successfully"})
            return JsonResponse({"error": "Payment not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)
