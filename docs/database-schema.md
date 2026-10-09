# Database Schema — Subscription & Billing Management System

## 1. Overview

The application uses PostgreSQL as its relational database. Django ORM manages database models, relationships, migrations, and database operations.

**Database name:** `subscription_billing_db`

**Database engine:** PostgreSQL

## 2. Tables

### 2.1 `auth_user`

Django's built-in User model stores authentication and basic user information.

| Field | Purpose |
|---|---|
| `id` | Primary key |
| `username` | Unique username |
| `password` | Hashed password |
| `first_name` | User's first name |
| `last_name` | User's last name |
| `email` | Email address |
| `is_active` | Whether the account is active |
| `is_staff` | Staff access flag |
| `is_superuser` | Superuser access flag |

Django manages additional authentication fields.

### 2.2 `accounts_customerprofile`

Stores customer-specific profile information.

| Field | Type / Description |
|---|---|
| `id` | Primary key |
| `user_id` | One-to-one foreign key to `auth_user` |
| `phone` | Optional phone number, maximum 20 characters |
| `created_at` | Automatically recorded creation timestamp |
| `updated_at` | Automatically updated modification timestamp |

**Relationship:** Each customer profile belongs to one Django user. A user can have at most one customer profile.

### 2.3 `plans_subscriptionplan`

Stores subscription plan details.

| Field | Type / Description |
|---|---|
| `id` | Primary key |
| `name` | Plan name, maximum 100 characters |
| `description` | Optional plan description |
| `price` | Decimal value with 10 total digits and 2 decimal places |
| `billing_cycle` | `MONTHLY` or `YEARLY` |
| `is_active` | Indicates whether the plan is available |
| `created_at` | Creation timestamp |
| `updated_at` | Last modification timestamp |

Inactive plans are retained in the database rather than physically deleted through the admin plan-management interface.

### 2.4 `subscriptions_subscription`

Stores customer subscriptions.

| Field | Type / Description |
|---|---|
| `id` | Primary key |
| `customer_id` | Foreign key to `accounts_customerprofile` |
| `plan_id` | Foreign key to `plans_subscriptionplan` |
| `status` | `TRIAL`, `ACTIVE`, `CANCELLED`, or `EXPIRED` |
| `start_date` | Subscription start timestamp |
| `end_date` | Optional subscription end timestamp |
| `created_at` | Creation timestamp |
| `updated_at` | Last modification timestamp |

**Relationships:**
- A customer can have multiple subscriptions.
- A plan can be associated with multiple subscriptions.
- Customer and plan deletion is protected while referenced by subscriptions.

### 2.5 `subscriptions_subscriptionhistory`

Records subscription lifecycle and plan changes.

| Field | Type / Description |
|---|---|
| `id` | Primary key |
| `subscription_id` | Foreign key to `subscriptions_subscription` |
| `previous_plan_id` | Optional foreign key to the previous plan |
| `new_plan_id` | Optional foreign key to the new plan |
| `action` | `CREATED`, `UPGRADED`, `DOWNGRADED`, `CANCELLED`, or `EXPIRED` |
| `details` | Optional descriptive information |
| `created_at` | Event creation timestamp |

A subscription can have multiple history records. Deleting a subscription deletes its associated history records.

### 2.6 `billing_payment`

Stores payment records. Payments are simulated; the application does not integrate with a real payment gateway.

| Field | Type / Description |
|---|---|
| `id` | Primary key |
| `customer_id` | Foreign key to `accounts_customerprofile` |
| `subscription_id` | Foreign key to `subscriptions_subscription` |
| `amount` | Payment amount, stored as a decimal |
| `payment_date` | Automatically recorded payment timestamp |
| `status` | `PENDING`, `SUCCESS`, or `FAILED` |
| `transaction_reference` | Unique transaction/reference identifier, maximum 100 characters |
| `payment_method` | Payment method, maximum 50 characters |

Customer and subscription deletion is protected while referenced by payments.

### 2.7 `billing_invoice`

Stores invoice information.

| Field | Type / Description |
|---|---|
| `id` | Primary key |
| `invoice_number` | Unique invoice identifier, maximum 50 characters |
| `customer_id` | Foreign key to `accounts_customerprofile` |
| `subscription_id` | Foreign key to `subscriptions_subscription` |
| `plan_id` | Foreign key to `plans_subscriptionplan` |
| `amount` | Invoice amount, stored as a decimal |
| `issue_date` | Automatically recorded issue timestamp |
| `due_date` | Invoice due timestamp |
| `status` | `PENDING`, `PAID`, or `CANCELLED` |

Customer, subscription, and plan deletion is protected while referenced by invoices.

## 3. Relationship Summary

- `auth_user` → `accounts_customerprofile`: one-to-one.
- `accounts_customerprofile` → `subscriptions_subscription`: one-to-many.
- `plans_subscriptionplan` → `subscriptions_subscription`: one-to-many.
- `subscriptions_subscription` → `subscriptions_subscriptionhistory`: one-to-many.
- `plans_subscriptionplan` → `subscriptions_subscriptionhistory`: referenced by previous and new plan fields.
- `accounts_customerprofile` → `billing_payment`: one-to-many.
- `subscriptions_subscription` → `billing_payment`: one-to-many.
- `accounts_customerprofile` → `billing_invoice`: one-to-many.
- `subscriptions_subscription` → `billing_invoice`: one-to-many.
- `plans_subscriptionplan` → `billing_invoice`: one-to-many.

## 4. Data Integrity

The application uses Django model relationships and database constraints to maintain data integrity.

- Primary keys uniquely identify records.
- User profiles have a one-to-one relationship with Django users.
- Invoice numbers and transaction references are unique.
- Decimal fields are used for monetary values.
- Foreign-key deletion policies protect referenced customers, plans, subscriptions, payments, and invoices as configured in the models.
- Status and billing-cycle choices are defined in the Django models.

Application-level validation and permission checks enforce additional business rules.

## 5. Database Setup

1. Install and start PostgreSQL.
2. Create the `subscription_billing_db` database.
3. Configure the database connection through the project's environment variables.
4. Install dependencies listed in `requirements.txt`.
5. Run database migrations:

   ```powershell
   python manage.py migrate
   ```

6. Verify the configuration:

   ```powershell
   python manage.py check
   ```

**Security note:** Database passwords and other secrets must remain in `.env`, which must not be committed to Git. Use `.env.example` to document required environment variables without real credentials.
