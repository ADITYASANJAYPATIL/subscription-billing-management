# API Documentation — Subscription & Billing Management System

## 1. Overview

The application provides REST APIs using Django REST Framework.

**Base URL (local development):** `http://127.0.0.1:8000`

**Authentication:** Token authentication for REST API requests.

Include the following header for authenticated requests:

```http
Authorization: Token YOUR_AUTH_TOKEN
```

JSON request bodies should use:

```http
Content-Type: application/json
```

### User roles

- **Admin:** Can manage subscription plans and view records across customers where permitted.
- **Customer:** Can access available plans, manage their own subscriptions, and view their own payments and invoices.

Unauthenticated requests are denied by the API's default authentication and permission configuration.

## 2. Plans API

Base path: `/api/plans/`

### GET `/api/plans/`

**Purpose:** List subscription plans.

**Permissions:** Authenticated Admin or Customer.

- Admins can view active and inactive plans.
- Customers can view active plans only.

**Success:** `200 OK`

Example response:

```json
[
  {
    "id": 1,
    "name": "Basic Plan",
    "description": "Basic subscription",
    "price": "499.00",
    "billing_cycle": "MONTHLY",
    "is_active": true,
    "created_at": "2026-10-08T10:00:00Z",
    "updated_at": "2026-10-08T10:00:00Z"
  }
]
```

The example values are illustrative.

### GET `/api/plans/{id}/`

**Purpose:** Retrieve a plan by ID.

**Permissions:** Authenticated Admin or Customer. Customers can retrieve active plans only.

**Success:** `200 OK`

An unavailable plan ID returns `404 Not Found`.

### POST `/api/plans/`

**Purpose:** Create a subscription plan.

**Permissions:** Admin only.

Example request:

```json
{
  "name": "Premium Plan",
  "description": "Premium subscription",
  "price": "999.00",
  "billing_cycle": "MONTHLY",
  "is_active": true
}
```

**Success:** `201 Created`

The response contains the created plan, including its generated ID and timestamps.

### PUT `/api/plans/{id}/`

**Purpose:** Update a subscription plan.

**Permissions:** Admin only.

Send the plan fields to update, including the required model fields.

**Success:** `200 OK`

An invalid request returns `400 Bad Request`. An unavailable plan returns `404 Not Found`.

### DELETE `/api/plans/{id}/`

**Purpose:** Deactivate a subscription plan.

**Permissions:** Admin only.

The implementation overrides deletion to set `is_active` to `false` rather than physically deleting the plan.

**Success:** `204 No Content`

## 3. Subscriptions API

Base path: `/api/subscriptions/`

### GET `/api/subscriptions/`

**Purpose:** List subscriptions.

**Permissions:** Admin or Customer.

- Admins can view subscriptions across customers.
- Customers can view only their own subscriptions.

**Success:** `200 OK`

### POST `/api/subscriptions/`

**Purpose:** Create a subscription.

**Permissions:** Customer only.

Example request:

```json
{
  "plan": 1
}
```

The customer is identified from the authenticated user. The client cannot set the customer, status, or start/end dates through the serializer.

The selected plan must be active. Successful creation also records an initial subscription-history event.

**Success:** `201 Created`

**Validation failure:** `400 Bad Request`

### GET `/api/subscriptions/{id}/`

**Purpose:** Retrieve a subscription by ID.

**Permissions:** Admin or the subscription's owning customer.

**Success:** `200 OK`

Customers cannot retrieve another customer's subscription. An object outside the customer's permitted queryset returns `404 Not Found`.

### POST `/api/subscriptions/{id}/upgrade/`

**Purpose:** Upgrade a subscription to a higher-priced plan.

**Permissions:** Owning customer only.

Example request:

```json
{
  "plan": 2
}
```

The target plan must exist, be active, and have a higher price than the current plan. Cancelled and expired subscriptions cannot be modified. A successful change creates a history record.

**Success:** `200 OK`

Invalid plan changes return `400 Bad Request`. A subscription not owned by the customer returns `404 Not Found`.

### POST `/api/subscriptions/{id}/downgrade/`

**Purpose:** Downgrade a subscription to a lower-priced plan.

**Permissions:** Owning customer only.

Example request:

```json
{
  "plan": 1
}
```

The target plan must be active and have a lower price than the current plan.

**Success:** `200 OK`

Invalid plan changes return `400 Bad Request`. A subscription not owned by the customer returns `404 Not Found`.

### POST `/api/subscriptions/{id}/cancel/`

**Purpose:** Cancel a subscription.

**Permissions:** Owning customer only.

The cancellation follows the application's immediate-cancellation rule. A successful cancellation records the change in subscription history.

**Success:** The exact response format depends on the cancellation view implementation.

Invalid cancellation attempts are rejected.

## 4. Payments API

Base path: `/api/payments/`

### GET `/api/payments/`

**Purpose:** List payment records.

**Permissions:** Admin or Customer.

- Admins can view payments across customers.
- Customers can view only their own payment records.

**Success:** `200 OK`

Example response:

```json
[
  {
    "id": 1,
    "customer": 2,
    "subscription": 3,
    "amount": "999.00",
    "payment_date": "2026-10-08T15:18:00Z",
    "status": "SUCCESS",
    "transaction_reference": "TXN-002",
    "payment_method": "CARD"
  }
]
```

The example values are illustrative.

### GET `/api/payments/{id}/`

**Purpose:** Retrieve a payment by ID.

**Permissions:** Admin or the payment's owning customer.

**Success:** `200 OK`

Customers cannot retrieve another customer's payment record.

### POST `/api/payments/simulate/`

**Purpose:** Create a simulated payment record.

**Permissions:** Customer only.

Example request:

```json
{
  "subscription": 3,
  "status": "SUCCESS",
  "transaction_reference": "TXN-004",
  "payment_method": "CARD"
}
```

Required fields:

- `subscription`
- `status`
- `transaction_reference`
- `payment_method`

Allowed statuses for this operation are `SUCCESS` and `FAILED`. The amount and customer are determined server-side.

Payments cannot be recorded for cancelled or expired subscriptions.

**Success:** `201 Created`

**Validation failure:** `400 Bad Request`

A subscription not found in the customer's permitted queryset returns `404 Not Found`.

**Important:** This endpoint simulates payments. It does not charge a real payment method or connect to a payment gateway.

## 5. Invoices API

Base path: `/api/invoices/`

### GET `/api/invoices/`

**Purpose:** List invoices.

**Permissions:** Admin or Customer.

- Admins can view invoices across customers.
- Customers can view only their own invoices.

**Success:** `200 OK`

Example response:

```json
[
  {
    "id": 1,
    "invoice_number": "INV-20261008-001",
    "customer": 2,
    "subscription": 3,
    "plan": 2,
    "amount": "999.00",
    "issue_date": "2026-10-08T15:00:00Z",
    "due_date": "2026-10-15T15:00:00Z",
    "status": "PENDING"
  }
]
```

The example values are illustrative.

### GET `/api/invoices/{id}/`

**Purpose:** Retrieve an invoice by ID.

**Permissions:** Admin or the invoice's owning customer.

**Success:** `200 OK`

Customers cannot retrieve another customer's invoice.

### POST `/api/invoices/create/`

**Purpose:** Generate an invoice for a subscription.

**Permissions:** Customer only.

Example request:

```json
{
  "subscription": 3
}
```

The subscription must belong to the authenticated customer and must not be cancelled or expired.

The invoice amount, plan, customer, invoice number, and due date are generated by the server-side invoice service. The client cannot set these fields through the serializer.

**Success:** `201 Created`

An omitted subscription ID returns `400 Bad Request`. A subscription not owned by the customer returns `404 Not Found`. A cancelled or expired subscription returns `400 Bad Request`.

## 6. Reports API

Base path: `/api/reports/`

Both endpoints require authentication and the Admin role.

### GET `/api/reports/subscriptions/`

**Purpose:** Retrieve total subscriptions and subscription counts grouped by status.

**Permissions:** Admin only.

**Success:** `200 OK`

Example response:

```json
{
  "total_subscriptions": 3,
  "subscriptions_by_status": [
    {
      "status": "CANCELLED",
      "count": 2
    },
    {
      "status": "TRIAL",
      "count": 1
    }
  ]
}
```

The returned statuses and counts depend on the current database.

### GET `/api/reports/revenue/`

**Purpose:** Retrieve revenue grouped by plan and by month.

**Permissions:** Admin only.

Only successful payments are included in the revenue calculations.

**Success:** `200 OK`

Example response:

```json
{
  "revenue_by_plan": [
    {
      "subscription__plan__id": 2,
      "subscription__plan__name": "Premium Plan",
      "total_revenue": "999.00"
    }
  ],
  "monthly_revenue": [
    {
      "month": "2026-10-01T00:00:00Z",
      "total_revenue": "999.00"
    }
  ]
}
```

The example values are illustrative. Actual numeric formatting and timestamp output depend on the serializer and Django configuration.

## 7. Common HTTP Status Codes

| Status | Meaning |
|---|---|
| `200 OK` | Request succeeded |
| `201 Created` | A resource was created |
| `204 No Content` | Request succeeded without a response body |
| `400 Bad Request` | Validation or business-rule failure |
| `401 Unauthorized` | Authentication is missing or invalid |
| `403 Forbidden` | Authenticated user lacks the required role |
| `404 Not Found` | Resource does not exist or is outside the permitted queryset |

The precise status code depends on the endpoint's implementation.

## 8. Security and Business Rules

- Authentication is required for protected API operations.
- Admin-only operations are protected by role permissions.
- Customer queries are restricted to the authenticated customer's records.
- Subscription creation accepts an active plan.
- Upgrade and downgrade operations validate the target plan and current subscription status.
- Subscription changes create history records.
- Payments are simulated; real payment processing is not integrated.
- Invoice amounts are derived server-side.
- Reports are restricted to administrators.
- Database credentials and API tokens must not be committed to the repository.

## 9. API Limitations

- No real payment gateway is integrated.
- No email or SMS notifications are provided.
- No tax, refund, coupon, or multi-currency processing is included.
- Background billing jobs and automatic recurring charges are not implemented.

These limitations reflect the assignment's intended scope.
