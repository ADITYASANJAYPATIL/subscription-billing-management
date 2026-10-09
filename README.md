# Subscription & Billing Management System

A Django-based web application for managing customers, subscription plans, subscriptions, payment records, invoices, and basic business reports.

## 1. Project Overview

This project was developed as part of a technical evaluation assignment. It provides separate interfaces for administrators and customers, with role-based access control and REST APIs.

### Key Features

- Customer account management
- Subscription plan creation and management
- Subscription creation, upgrade, downgrade, and cancellation
- Subscription status and history tracking
- Simulated payment records
- Invoice generation and management
- Subscription and revenue reports
- REST APIs using Django REST Framework
- Role-based access control for administrators and customers
- PostgreSQL database integration

## 2. Technology Stack

- **Backend:** Python, Django
- **REST APIs:** Django REST Framework
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, JavaScript, Django Templates
- **API Documentation:** Django REST Framework and configured API schema tools

## 3. Requirements

Install the following before running the project:

- Python 3.12
- PostgreSQL
- Git
- pip

## 4. Installation and Setup

### Step 1: Clone the repository

```bash
git clone https://github.com/ADITYASANJAYPATIL/subscription-billing-management.git
cd subscription-billing-management
```


If you already have the project downloaded, open its project directory instead.

### Step 2: Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure PostgreSQL

Create a PostgreSQL database named:

```text
subscription_billing_db
```

Configure the database connection using the environment variables expected by `config/settings.py`. Refer to `.env.example` for the required variable names and format.

Create a local `.env` file containing your own database connection settings. Do not commit real passwords or other secrets to Git.

### Step 5: Apply database migrations

```powershell
python manage.py migrate
```

### Step 6: Create an administrator account if required

```powershell
python manage.py createsuperuser
```

Assign the appropriate application role to the user according to the project's role configuration.

### Step 7: Start the development server

```powershell
python manage.py runserver
```

Open the application at:

http://127.0.0.1:8000/login/

Use the configured login page to sign in.

## 5. Application Pages

### Customer Interface

- Customer dashboard
- Available subscription plans
- Customer subscriptions and subscription details
- Upgrade and downgrade actions
- Subscription cancellation
- Payment records
- Invoice records

### Administrator Interface

- Admin dashboard
- Customer management
- Subscription plan management
- All-customer subscription listing
- Payment management
- Invoice management
- Subscription and revenue reports

## 6. REST API Overview

The application includes REST API endpoints for plans, subscriptions, payments, invoices, and reports.

The principal endpoint groups are:

| Resource | Endpoint prefix |
|---|---|
| Subscription plans | `/api/plans/` |
| Subscriptions | `/api/subscriptions/` |
| Payments | `/api/payments/` |
| Invoices | `/api/invoices/` |
| Reports | `/api/reports/` |

Authentication and permissions depend on the endpoint and user role. Customers must only access their own subscription, payment, and invoice records. Administrative operations are restricted to authorized administrators.

Refer to `docs/api-documentation.md` for the detailed endpoint reference, request formats, response formats, and permission rules.

## 7. Database

The application uses PostgreSQL.

The main application entities include:

- User
- CustomerProfile
- SubscriptionPlan
- Subscription
- SubscriptionHistory
- Payment
- Invoice

The Django migration files define the database schema. Additional database information and entity relationships are documented in `docs/database-schema.md`.

## 8. SQL Reporting Queries

SQL reporting queries are maintained in:

```text
sql/reports.sql
```

The queries cover:

- Subscription counts by status
- Successful revenue by subscription plan
- Monthly successful revenue
- Active subscriptions
- Cancelled and expired subscriptions

These queries are written for PostgreSQL.

## 9. Testing

Run Django's configuration and model checks:

```powershell
python manage.py check
```

Run the project's automated tests:

```powershell
python manage.py test
```

Manual functional, API, workflow, and permission test cases are documented in `docs/manual-test-cases.md`.

Only tests actually executed should be reported as passed in the final submission.

## 10. Security and Access Control

- Authentication is required for protected application functionality.
- Administrator and customer roles have different permissions.
- Customer data access is restricted by ownership.
- Server-side validation is used for business rules.
- Database credentials and secrets must be stored in local environment configuration rather than source code.

## 11. Known Limitations

The system is designed for a basic subscription and billing workflow. The following capabilities are outside the current assignment scope:

- Real payment gateway integration
- Automated email and SMS notifications
- GST and tax calculations
- Coupons and discounts
- Refund processing
- Multiple currency support
- Complex prorated billing
- Background billing jobs
- Third-party authentication
- Mobile application
- Advanced analytics and multi-tenant architecture

Payment processing is simulated; the application does not charge real money.

## 12. Project Structure

```text
subscription-billing-management/
├── accounts/
├── billing/
├── config/
├── docs/
│   ├── api-documentation.md
│   ├── database-schema.md
│   └── manual-test-cases.md
├── plans/
├── reports/
├── sql/
│   └── reports.sql
├── static/
├── subscriptions/
├── templates/
│   ├── admin/
│   └── customer/
├── .env.example
├── .gitignore
├── Development_Progress_Tracker_Subscription_Billing_System_Final.docx
├── SRS_Subscription_Billing_Management_System.docx
├── manage.py
├── README.md
└── requirements.txt
```


## 13. Additional Documentation

- `SRS_Subscription_Billing_Management_System.docx` — original software requirements specification, Version 1.0.
- `Development_Progress_Tracker_Subscription_Billing_System.docx` — development checkpoints, validation evidence, and remaining submission tasks.
- `docs/api-documentation.md` — REST API reference.
- `docs/database-schema.md` — database entities and relationships.
- `docs/manual-test-cases.md` — manual functional, API, and security tests.
- `sql/reports.sql` — PostgreSQL reporting queries.

## 14. Running the Application

After configuring the environment, installing dependencies, and applying migrations, start the development server:

```powershell
python manage.py runserver
```

This runs the application in Django's local development environment. For production deployment, configure appropriate production security settings, database credentials, and hosting infrastructure.