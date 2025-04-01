# Restaurant Management System

A modern web application for restaurant management built with FastAPI, SQLite, and Jinja2.

## Features

- User and Admin authentication
- Order management system
- Product catalog
- Real-time order tracking
- Dashboard with analytics
- Table/reservation management
- Inventory control

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

## Project Structure

```
restaurant_app/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── auth.py
│   └── routers/
│       ├── auth.py
│       ├── orders.py
│       ├── products.py
│       └── admin.py
├── static/
│   ├── css/
│   └── js/
└── templates/
    ├── auth/
    ├── admin/
    └── user/
```
