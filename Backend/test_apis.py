import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def request(path, method="GET", data=None):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method=method)
    req.add_header("Content-Type", "application/json")
    
    body = None
    if data:
        body = json.dumps(data).encode("utf-8")
        
    try:
        with urllib.request.urlopen(req, data=body) as response:
            res_body = response.read().decode("utf-8")
            return response.status, json.loads(res_body) if res_body else None
    except urllib.error.HTTPError as e:
        res_body = e.read().decode("utf-8")
        try:
            err_data = json.loads(res_body)
        except Exception:
            err_data = res_body
        return e.code, err_data
    except Exception as e:
        return 0, str(e)

def run_tests():
    print("Starting API Verification Tests for Taxi Booking Application...")
    
    # Pre-test database cleaning
    print("Resetting database states...")
    request("/customers/delete/101/", "DELETE")
    request("/drivers/delete/201/", "DELETE")
    request("/vehicles/delete/301/", "DELETE")
    request("/bookings/delete/401/", "DELETE")
    request("/payments/delete/501/", "DELETE")

    # 1. Test Customers
    print("\n--- Customers API ---")
    c_data = {
        "customer_id": 101,
        "full_name": "Rahul Sharma",
        "email": "rahul@gmail.com",
        "phone": "9876543210",
        "address": "Hyderabad",
        "password": "rahul123"
    }
    status, res = request("/customers/add/", "POST", c_data)
    print(f"POST /customers/add/: Status {status}, Res: {res}")
    if status != 201:
        print("FAIL: Add Customer failed")
        sys.exit(1)
        
    cust_id = res["customer_id"]
    
    status, res = request("/customers/")
    print(f"GET /customers/: Status {status}, Res length: {len(res) if isinstance(res, list) else 'Error'}")
    if status != 200:
        print("FAIL: Get Customers failed")
        sys.exit(1)
        
    c_update = {"phone": "9999999999"}
    status, res = request(f"/customers/update/{cust_id}/", "PUT", c_update)
    print(f"PUT /customers/update/{cust_id}/: Status {status}, Res: {res}")
    if status != 200:
        print("FAIL: Update Customer failed")
        sys.exit(1)

    # 2. Test Drivers
    print("\n--- Drivers API ---")
    d_data = {
        "driver_id": 201,
        "driver_name": "Ramesh Kumar",
        "email": "ramesh@gmail.com",
        "phone": "9988776655",
        "license_number": "DL123456789",
        "experience": 5,
        "availability": "Available"
    }
    status, res = request("/drivers/add/", "POST", d_data)
    print(f"POST /drivers/add/: Status {status}, Res: {res}")
    if status != 201:
        print("FAIL: Add Driver failed")
        sys.exit(1)
        
    drv_id = res["driver_id"]
    
    status, res = request("/drivers/")
    print(f"GET /drivers/: Status {status}, Res length: {len(res) if isinstance(res, list) else 'Error'}")
    if status != 200:
        print("FAIL: Get Drivers failed")
        sys.exit(1)
        
    d_update = {"availability": "Busy"}
    status, res = request(f"/drivers/update/{drv_id}/", "PUT", d_update)
    print(f"PUT /drivers/update/{drv_id}/: Status {status}, Res: {res}")
    if status != 200:
        print("FAIL: Update Driver failed")
        sys.exit(1)

    # 3. Test Vehicles
    print("\n--- Vehicles API ---")
    v_data = {
        "vehicle_id": 301,
        "driver_name": "Ramesh Kumar",
        "vehicle_type": "Sedan",
        "vehicle_number": "TS09AB1234",
        "seating_capacity": 4,
        "model": "Hyundai Verna"
    }
    status, res = request("/vehicles/add/", "POST", v_data)
    print(f"POST /vehicles/add/: Status {status}, Res: {res}")
    if status != 201:
        print("FAIL: Add Vehicle failed")
        sys.exit(1)
        
    veh_id = res["vehicle_id"]
    
    status, res = request("/vehicles/")
    print(f"GET /vehicles/: Status {status}, Res length: {len(res) if isinstance(res, list) else 'Error'}")
    if status != 200:
        print("FAIL: Get Vehicles failed")
        sys.exit(1)
        
    v_update = {"model": "Hyundai Verna Facelift"}
    status, res = request(f"/vehicles/update/{veh_id}/", "PUT", v_update)
    print(f"PUT /vehicles/update/{veh_id}/: Status {status}, Res: {res}")
    if status != 200:
        print("FAIL: Update Vehicle failed")
        sys.exit(1)

    # 4. Test Bookings
    print("\n--- Bookings API ---")
    b_data = {
        "booking_id": 401,
        "customer_name": "Rahul Sharma",
        "driver_name": "Ramesh Kumar",
        "pickup_location": "Madhapur",
        "drop_location": "Gachibowli",
        "booking_date": "2026-08-15",
        "fare": 350.0,
        "ride_status": "Accepted"
    }
    status, res = request("/bookings/add/", "POST", b_data)
    print(f"POST /bookings/add/: Status {status}, Res: {res}")
    if status != 201:
        print("FAIL: Add Booking failed")
        sys.exit(1)
        
    book_id = res["booking_id"]
    
    status, res = request("/bookings/")
    print(f"GET /bookings/: Status {status}, Res length: {len(res) if isinstance(res, list) else 'Error'}")
    if status != 200:
        print("FAIL: Get Bookings failed")
        sys.exit(1)
        
    b_update = {"ride_status": "Completed"}
    status, res = request(f"/bookings/update/{book_id}/", "PUT", b_update)
    print(f"PUT /bookings/update/{book_id}/: Status {status}, Res: {res}")
    if status != 200:
        print("FAIL: Update Booking failed")
        sys.exit(1)

    # 5. Test Payments
    print("\n--- Payments API ---")
    p_data = {
        "payment_id": 501,
        "booking_id": 401,
        "customer_name": "Rahul Sharma",
        "amount": 350.0,
        "payment_method": "UPI",
        "payment_status": "Success",
        "transaction_id": "TXN456789123",
        "payment_date": "2026-08-15"
    }
    status, res = request("/payments/add/", "POST", p_data)
    print(f"POST /payments/add/: Status {status}, Res: {res}")
    if status != 201:
        print("FAIL: Add Payment failed")
        sys.exit(1)
        
    pay_id = res["payment_id"]
    
    status, res = request("/payments/")
    print(f"GET /payments/: Status {status}, Res length: {len(res) if isinstance(res, list) else 'Error'}")
    if status != 200:
        print("FAIL: Get Payments failed")
        sys.exit(1)
        
    p_update = {"payment_status": "Success"}
    status, res = request(f"/payments/update/{pay_id}/", "PUT", p_update)
    print(f"PUT /payments/update/{pay_id}/: Status {status}, Res: {res}")
    if status != 200:
        print("FAIL: Update Payment failed")
        sys.exit(1)

    # 6. Test Authentication API
    print("\n--- Authentication API ---")
    login_data = {
        "role": "customer",
        "email": "rahul@gmail.com",
        "password": "rahul123"
    }
    status, res = request("/api/login/", "POST", login_data)
    print(f"POST /api/login/ (Customer): Status {status}, Res message: {res.get('message')}")
    if status != 200:
        print("FAIL: Customer Login failed")
        sys.exit(1)

    login_data_driver = {
        "role": "driver",
        "email": "ramesh@gmail.com",
        "password": "9988776655" # using phone as pass
    }
    status, res = request("/api/login/", "POST", login_data_driver)
    print(f"POST /api/login/ (Driver): Status {status}, Res message: {res.get('message')}")
    if status != 200:
        print("FAIL: Driver Login failed")
        sys.exit(1)

    # 7. Test Dashboard Stats
    print("\n--- Dashboard Stats API ---")
    status, res = request("/api/stats/")
    print(f"GET /api/stats/: Status {status}, Earnings: Rs. {res.get('total_earnings')}, Bookings: {res.get('total_bookings')}")
    if status != 200:
        print("FAIL: Get Dashboard Stats failed")
        sys.exit(1)

    # 8. Cleanup Test Records
    print("\n--- Deleting test records for clean DB ---")
    request(f"/customers/delete/{cust_id}/", "DELETE")
    request(f"/drivers/delete/{drv_id}/", "DELETE")
    request(f"/vehicles/delete/{veh_id}/", "DELETE")
    request(f"/bookings/delete/{book_id}/", "DELETE")
    request(f"/payments/delete/{pay_id}/", "DELETE")

    print("\nALL API TESTS PASSED SUCCESSFULLY! (100% PASS)")

if __name__ == "__main__":
    run_tests()
