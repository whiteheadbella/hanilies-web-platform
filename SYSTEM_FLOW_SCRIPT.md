# Hanilies Cakeshoppe Event System Script and Architecture Guide

## 1) System Flow Script (End-to-End)

### Script A: Standard Order-to-Payment Lifecycle

1. User opens Home page (`/products/home/`) and browses packages/customizations.
2. User selects an event package or customization and adds to cart.
3. Cart computes running total using `unit_price * quantity` per line item.
4. User goes to Checkout (`/orders/cart/checkout/`).
5. System validates booking form fields (event date/time, venue, delivery profile).
6. System creates:
   - `Order` with status `PENDING`
   - `OrderDetail` records from cart items
   - `Booking` linked to order with delivery snapshot
7. System clears cart and stores session marker `checkout_confirmed_booking_id`.
8. User clicks **Pay Now** and opens payment page (`/payments/create/<booking_id>/`).
9. User submits payment method (GCash / Bank Transfer / Cash).
10. System creates `Payment` record, marks payment `PAID`, and updates:
    - `Order.status -> CONFIRMED`
    - `Booking.status -> CONFIRMED`
11. System clears `checkout_confirmed_booking_id` from session.
12. User is redirected to **My Orders** and can view updated status.

---

## 2) User Flow Script (Customer)

### Script B: Customer Journey

1. Register/Login.
2. Browse `Event Packages` and `Customization`.
3. Select package inclusions and optional quantities (where applicable).
4. Add items to cart and review itemized preview.
5. Proceed to checkout and submit booking details.
6. Confirm order then proceed to payment.
7. Submit payment method.
8. Track order in **My Orders** and payment history in **My Payments**.
9. Receive updates through notifications.

### Script C: Customer Error/Guard Flow

1. If cart is empty and user opens checkout: system redirects back to cart with message.
2. If order is already not pending, payment endpoint blocks duplicate payment and redirects safely.
3. If user tries accessing another user’s booking/payment route, access is denied.

---

## 3) RBAC Flow Script (interpreting “ROBC” as RBAC)

### Roles Used

- **Customer**: shop, checkout, pay, view own orders/payments.
- **Manager/Admin-like role**: manage products, packages, gallery/customization, monitor orders/bookings.

### Script D: Authorization Flow

1. User logs in.
2. `accounts.context_processors.role_flags` injects role flags into templates.
3. Views check role/ownership using permission helpers (e.g., manager checks, order ownership checks).
4. If authorized: request continues.
5. If unauthorized: system returns `access_denied.html` or redirects with message.

### Script E: Data Access Boundary

- Customer can only read/write records tied to their own account (cart/order/booking/payment).
- Manager can access operational/management pages and perform catalog/order management actions.

---

## 4) Admin / Manager Flow Script

### Script F: Daily Operations

1. Login as manager.
2. Open dashboard and review order/bookings counts.
3. Manage product catalog (cakes, packages, package inclusions).
4. Manage gallery/home visuals.
5. Review customer orders and statuses (`PENDING`, `CONFIRMED`, etc.).
6. Use notifications/audit trail for traceability.

### Script G: Package Management

1. Create/update package metadata.
2. Add/update package inclusions and `unit_price`.
3. Activate/deactivate package visibility.
4. Validate customer-side rendering in package tabs.

---

## 5) SDLC Approach for This System

### Recommended SDLC Model

**Agile Iterative (Scrum-style, short cycles)**

Why this fits:

- UI/UX and flow requirements changed frequently.
- Incremental deployment of features (checkout, payment, gallery, package logic).
- Continuous feedback and rapid adjustment are needed.

### Suggested SDLC Phases Used

1. **Requirements & backlog** (feature stories, issue list)
2. **Design** (DB + flow + template/view design)
3. **Build** (incremental coding in apps)
4. **Test** (smoke tests, regression checks, user acceptance)
5. **Deploy** (staging/production)
6. **Monitor & improve** (logs, audit, bug fixes)

---

## 6) Tools, Technologies, and Methodologies

### Frontend

- Django Templates (server-rendered HTML)
- Bootstrap-based UI (plus `crispy-bootstrap5`)
- `django-crispy-forms` for consistent form rendering

### Backend

- Python + Django 5.0.1
- App modules: `accounts`, `products`, `customization`, `orders`, `payments`, `notifications`, `audit`, `scheduling`
- Django auth/session/messages middleware

### Database

- PostgreSQL (`django.db.backends.postgresql` in settings)
- Core entities: `Order`, `OrderDetail`, `Booking`, `Payment`, `CartItem`, `EventPackage`, `EventPackageItem`, user/address profiles

### Supporting Libraries / Infra

- `pillow` for image handling
- `python-decouple` for env configuration support
- `whitenoise` for static file serving strategy
- Django migration system for schema versioning

### Engineering Methodologies

- **MVC/MVT pattern** (Django Model-Template-View)
- **RBAC/ownership authorization checks**
- **Incremental feature delivery**
- **Smoke testing for critical user paths**
- **Audit logging and notifications for traceability**

---

## 7) Suggested Process Script for Team Use

1. Pick feature from backlog.
2. Define acceptance criteria (happy path + edge cases).
3. Update model/view/template minimally.
4. Run migrations and checks.
5. Execute smoke path:
   - browse -> add to cart -> checkout -> confirm -> pay -> verify status/session cleanup.
6. Demo and collect user feedback.
7. Iterate next sprint.

---

## 8) Notes

- If you intended **ROBC** as a different acronym (not RBAC), replace Section 3 label and I can rewrite that section precisely.
- For production hardening, move secrets to environment variables and set secure `ALLOWED_HOSTS` + `DEBUG=False`.

---

## 9) Trial Deployment Script (Render)

### A. One-Time Prep (already added in project)

- `Procfile`
- `build.sh`
- `runtime.txt`
- Environment-based Django settings (`DEBUG`, `ALLOWED_HOSTS`, DB vars)

### B. Push to GitHub

```bash
git init
git add .
git commit -m "trial deployment setup"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

### C. Create Render Web Service (Trial)

1. Open Render Dashboard -> **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Use these settings:
   - **Runtime**: Python 3
   - **Build Command**: `bash build.sh`
   - **Start Command**: `gunicorn hanilies_cakeshoppe_event.wsgi:application --bind 0.0.0.0:$PORT`

### D. Set Environment Variables in Render

Set these in Render -> Service -> Environment:

```text
DEBUG=False
SECRET_KEY=<generate-strong-secret>
ALLOWED_HOSTS=<your-render-service>.onrender.com
CSRF_TRUSTED_ORIGINS=https://<your-render-service>.onrender.com

DB_NAME=hanilies
DB_USER=hanilies_user
DB_PASSWORD=<your-db-password>
DB_HOST=<your-db-host>
DB_PORT=5432
```

> If you are still using your existing Render PostgreSQL instance, keep its current DB values.

### E. Deploy and Verify

1. Click **Manual Deploy -> Deploy latest commit**.
2. Wait until build and deploy finish.
3. Open URL: `https://<your-render-service>.onrender.com/products/home/`
4. Quick smoke checklist after deployment:
   - Register/Login works
   - Add package to cart works
   - Checkout confirm works
   - Payment submit works
   - Order status changes to `CONFIRMED`

### F. Trial Rollback / Re-Deploy

If deployment fails after a new commit:

1. Open Render -> **Events** and identify failed deploy log.
2. Revert locally:

```bash
git log --oneline
git revert <bad-commit-hash>
git push origin main
```

3. Redeploy from latest successful commit.

### G. Optional Local Trial Script Before Push

```bash
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

### H. One-Click Blueprint Deploy (using `render.yaml`)

1. Commit and push `render.yaml` to GitHub.
2. In Render Dashboard, click **New +** -> **Blueprint**.
3. Select your repository and branch.
4. Render auto-detects `render.yaml` and creates:
   - Web service: `hanilies-cakeshoppe-event`
   - PostgreSQL database: `hanilies-db`
5. Click **Apply** to deploy.
6. After deployment, open your generated URL:
   - `https://<your-service-name>.onrender.com/products/home/`

---

## 10) Quick Local Restart (After Closing VS Code)

- Double-click `start_system.bat` in the project root.
- It will:
  1.  Activate `venv`
  2.  Run `python manage.py migrate`
  3.  Open `http://127.0.0.1:8000/`
  4.  Start Django server
