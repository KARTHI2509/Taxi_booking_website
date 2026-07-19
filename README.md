# CabGo - Taxi Booking Application

CabGo is a state-of-the-art Taxi Booking platform developed using **Django REST APIs** for the backend and a premium **HTML/CSS/JS** glassmorphic interface on the frontend. The project structure separates concerns cleanly by packaging logic inside multiple Django apps (`customers`, `drivers`, `vehicles`, `bookings`, `payments`, `dashboard`) while centralizing all route URL configurations in the core backend module.

The application includes a **dual-mode database manager**: it connects seamlessly to a cloud **MongoDB Atlas** cluster if a connection URI is provided, and gracefully falls back to a zero-configuration local **SQLite** database otherwise. This makes the application completely plug-and-play for local development, while remaining fully persistent and production-ready for Render deployment.

---

## 🚀 Key Features
- **Hero Banner & Offers**: Elegant home screen displaying popular destinations and discount promo codes.
- **Unified Login**: A single login portal for Customers, Drivers, and Administrators.
- **Customer Dashboard**: Overview of booking history, payment transactions, and active rides.
- **Ride Booking Engine**: Interactive panel with automatic fare estimates based on distance and selected vehicle type (Bike, Auto, Sedan, SUV, etc.).
- **Driver Console**: Operators can update availability (Available, Busy, Offline), accept ride requests, start trips, and track earnings.
- **Master Admin Console**: Admin controls allowing full CRUD operations (Create, Read, Update, Delete) on Customers, Drivers, Vehicles, Bookings, and Payments using popup modals.

---

## 📂 Project Structure
```
TaxiBookingApplication/
│
├── Backend/
│   ├── build.sh                 # Render build script
│   ├── db.py                    # Dual-mode DB adapter (MongoDB / SQLite)
│   ├── local_db.sqlite3         # Fallback SQLite DB (auto-generated)
│   ├── manage.py                # Django CLI entrypoint
│   ├── Procfile                 # Deployment configurations
│   ├── requirements.txt         # Project package dependencies
│   ├── test_apis.py             # Automated API test suite
│   ├── .env                     # Configuration variables
│   │
│   ├── taxi_booking/            # Core settings & URLs
│   │   ├── settings.py
│   │   └── urls.py
│   │
│   ├── customers/               # Customer app module
│   │   └── views.py
│   ├── drivers/                 # Driver app module
│   │   └── views.py
│   ├── vehicles/                # Vehicle app module
│   │   └── views.py
│   ├── bookings/                # Bookings app module
│   │   └── views.py
│   ├── payments/                # Payments app module
│   │   └── views.py
│   └── dashboard/               # Auth & dashboard stats app module
│       └── views.py
│
└── Frontend/
    ├── index.html               # Home page
    ├── login.html               # Unified Login form
    ├── register.html            # Registration form
    ├── booking.html             # Ride selector & estimator
    ├── drivers.html             # Fleet listings
    ├── payments.html            # Payment transaction checkouts
    ├── ride_history.html        # Track previous and active rides
    ├── customer_dashboard.html  # Customer account metrics
    ├── driver_dashboard.html    # Driver availability & trip details
    ├── admin_dashboard.html     # Administrator master tables
    ├── style.css                # Premium glassmorphic theme styling
    └── script.js                # Reusable Fetch API communication wrapper
```

---

## ⚙️ Installation & Running Local Development

### 1. Requirements
Ensure you have Python 3.x installed. Open your terminal in the `Backend/` directory and install dependencies:
```powershell
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` or create it:
```ini
MONGO_URI=
DATABASE_NAME=taxi_booking_db
SECRET_KEY=django-insecure-taxi-booking-secret-key-48392
DEBUG=True
ALLOWED_HOSTS=*
```
*Note: If `MONGO_URI` is left blank or cannot connect, CabGo automatically generates `local_db.sqlite3` and executes SQLite queries.*

### 3. Run Development Server
Start the Django development server:
```powershell
python manage.py runserver
```
The server will run at `http://127.0.0.1:8000/`. You can navigate to this URL in your web browser.

---

## 🧪 Testing the APIs
An automated python script `test_apis.py` is included in the `Backend/` folder. It performs more than 20+ operations including adding, updating, searching, and deleting records across all modules.

With the server running at `http://127.0.0.1:8000/`, open a new terminal window in the `Backend/` directory and execute:
```powershell
python test_apis.py
```
If everything is correctly configured, all tests will verify and return a completion message.

---

## ☁️ Deployment Instructions

### Render (Backend API & Static hosting)
1. Commit the codebase to a GitHub repository.
2. In the Render Dashboard, create a new **Web Service** connected to your repository.
3. Configure the environment:
   - **Runtime**: `Python`
   - **Build Command**: `./build.sh` (or `pip install -r requirements.txt && python manage.py collectstatic --noinput`)
   - **Start Command**: `gunicorn taxi_booking.wsgi`
4. Under **Environment Variables**, define your production settings:
   - `MONGO_URI`: Your MongoDB Atlas connection URI string.
   - `DATABASE_NAME`: `taxi_booking_db`
   - `SECRET_KEY`: A secure random password.
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `your-render-domain.onrender.com`
