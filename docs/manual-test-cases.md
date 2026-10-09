# Manual Test Cases — Subscription & Billing Management System

## 1. Test Environment

- **Framework:** Django and Django REST Framework
- **Database:** PostgreSQL
- **API testing tool:** Postman
- **Base URL:** `http://127.0.0.1:8000`
- **Test roles:** Admin and Customer
- **Authentication:** Token authentication for REST APIs

## 2. Test Cases

| ID | Test Scenario | Steps / Test Data | Expected Result |
|---|---|---|---|
| TC01 | Admin login | Log in with valid Admin credentials. | Admin dashboard opens. |
| TC02 | Invalid login | Submit an incorrect username or password. | Login is rejected with an error message. |
| TC03 | Customer login | Log in with valid Customer credentials. | Customer dashboard opens. |
| TC04 | Create customer | Admin submits valid customer details. | Customer account and profile are created. |
| TC05 | Duplicate customer username | Try to create a customer with an existing username. | Creation is rejected. |
| TC06 | Create plan | Admin creates a plan with valid name, price and billing cycle. | Plan is created successfully. |
| TC07 | Customer creates plan | Customer sends `POST /api/plans/`. | Request is denied. |
| TC08 | View active plans | Customer sends `GET /api/plans/`. | Only active plans are returned. |
| TC09 | View inactive plans | Admin sends `GET /api/plans/`. | Active and inactive plans are returned. |
| TC10 | Subscribe to active plan | Customer sends `POST /api/subscriptions/` with an active plan ID. | Subscription is created with the initial status and history entry. |
| TC11 | Subscribe to inactive plan | Customer attempts to subscribe to an inactive plan. | Request is rejected. |
| TC12 | Create subscription without authentication | Send `POST /api/subscriptions/` without a token. | Request is denied. |
| TC13 | View own subscription | Customer requests their own subscription ID. | Subscription details are returned. |
| TC14 | View another customer's subscription | Customer requests a subscription belonging to another customer. | Access is denied; the implementation returns `404 Not Found` for an object outside the permitted queryset. |
| TC15 | Upgrade subscription | Customer upgrades to a higher-priced active plan. | Plan is changed and history is recorded. |
| TC16 | Invalid upgrade | Attempt to upgrade to a plan with an equal or lower price. | Request is rejected. |
| TC17 | Downgrade subscription | Customer changes to a lower-priced active plan. | Plan is changed and history is recorded. |
| TC18 | Invalid downgrade | Attempt to downgrade to a plan with an equal or higher price. | Request is rejected. |
| TC19 | Cancel subscription | Customer cancels an eligible subscription. | Subscription is cancelled immediately and history is recorded. |
| TC20 | Cancel subscription twice | Attempt to cancel an already-cancelled subscription. | Request is rejected. |
| TC21 | Simulate successful payment | Submit a valid payment simulation with status `SUCCESS`. | Payment record is created using the server-calculated amount. |
| TC22 | Simulate failed payment | Submit a valid payment simulation with status `FAILED`. | Failed payment record is created. |
| TC23 | Generate invoice | Customer creates an invoice for their eligible subscription. | Invoice is created and its amount matches the plan price. |
| TC24 | Access another customer's invoice | Customer requests another customer's invoice. | Access is denied. |
| TC25 | Customer accesses reports | Customer requests `GET /api/reports/subscriptions/`. | Request is denied because reports are Admin-only. |
| TC26 | Admin accesses reports | Admin requests subscription and revenue reports. | Report data is returned. |
| TC27 | View own payments | Customer requests `GET /api/payments/`. | Only that customer's payment records are returned. |
| TC28 | View own invoices | Customer requests `GET /api/invoices/`. | Only that customer's invoices are returned. |
| TC29 | Payment on cancelled subscription | Attempt to simulate a payment for a cancelled subscription. | Request is rejected. |
| TC30 | Invoice amount protection | Attempt to provide a client-controlled invoice amount. | The serializer does not allow the client to set the invoice amount. |

## 3. Test Execution Record

Complete this section after running each test. Do not mark a test as passed unless its actual result has been checked.

| Test IDs | Actual Result | Status | Notes |
|---|---|---|---|
| TC01–TC05 | To be recorded | Not yet verified | Authentication and customer management |
| TC06–TC09 | To be recorded | Not yet verified | Plan management and permissions |
| TC10–TC14 | To be recorded | Not yet verified | Subscription creation and ownership |
| TC15–TC20 | To be recorded | Not yet verified | Upgrade, downgrade and cancellation |
| TC21–TC24 | To be recorded | Not yet verified | Payments and invoices |
| TC25–TC30 | To be recorded | Not yet verified | Reports and security |

## 4. Notes

- Run API tests using valid Admin and Customer tokens.
- Use two different customer accounts when testing object ownership.
- Use active and inactive plans to verify plan restrictions.
- Record actual HTTP status codes and response bodies for negative tests.
- Payment processing is simulated; no real payment gateway is connected.
- These are test cases, not evidence that every test has already passed.
