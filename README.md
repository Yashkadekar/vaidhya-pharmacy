# Vaidhya Pharmacy — Full-stack development project

A responsive pharmacy storefront and a separate role-protected admin workspace.

## Included

### Customer storefront
- Responsive home page, product catalogue, search and category browsing
- Customer registration and login
- Shopping cart and cash-on-delivery order placement
- Prescription upload (PDF/JPG/PNG, size-limited)
- Customer order history and status tracking

### Admin panel (`/admin`)
- Server-authorized admin access (customer role is rejected by every admin API)
- Dashboard metrics and operational attention queue
- Order list and status management
- Product create, edit and deactivate controls
- Inventory view with low-stock indicators
- Prescription queue, secure admin-only file download, approve/reject actions
- Customer directory and order counts
- Basic order status report and CSV export

## Technology
- Frontend: React 18, Vite, React Router, Axios, Lucide icons, CSS
- Backend: FastAPI, SQLAlchemy, SQLite (development), JWT, password hashing
- Uploaded prescriptions are stored outside the public frontend and served only through an admin-authenticated endpoint.

## Run locally

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env` and set a unique long `SECRET_KEY`, `ADMIN_EMAIL`, and a strong `ADMIN_PASSWORD`. Then run:

```bash
python seed_admin.py
python seed_catalog.py
uvicorn app.main:app --reload
```

API docs: http://127.0.0.1:8000/docs

### 2. Frontend (new terminal)

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:5173. Admin sign-in uses the credentials set in the backend `.env`; open http://localhost:5173/admin after signing in.

## Important configuration

- `SECRET_KEY`: replace the development value with a cryptographically random secret.
- `ADMIN_EMAIL` / `ADMIN_PASSWORD`: used only by the one-time admin seeding script. Never commit `.env` or share admin credentials.
- `DATABASE_URL`: defaults to local SQLite. Use managed PostgreSQL for deployment.
- `UPLOAD_DIR`: private prescription storage directory. Keep it outside any public static directory and back it up securely.
- `FRONTEND_ORIGIN`: exact frontend origin allowed by CORS.

## Not connected yet — credentials and professional review required

This is a development build, not a production pharmacy or payment service. These integrations are intentionally not faked:

1. **Online payments:** add Razorpay/PayU using server-side order creation, signature verification and verified webhooks. Do not collect card details yourself.
2. **Delivery:** connect a courier aggregator or delivery provider and persist real tracking events.
3. **Notifications:** configure a transactional email/SMS/WhatsApp provider and templates.
4. **Prescription workflow:** a licensed pharmacist must review prescriptions and dispensing must comply with applicable Indian law. The approval buttons are operational workflow controls, not a substitute for professional review.
5. **Production security:** move JWTs to secure HttpOnly cookies, add CSRF protections, rate limiting, audit trails, malware scanning, upload retention/deletion rules, HTTPS, backups, monitoring and managed object storage.
6. **Commerce readiness:** verify every catalogue item, image, price, stock quantity, tax treatment, delivery zone, returns policy and legal page. Add GST invoices and refund handling.
7. **Accessibility and QA:** test with real devices, screen readers, low bandwidth, and security testing before public launch.

Prescription file access is restricted to an authenticated admin role at the API layer. The admin page being hidden from customer navigation is not the security boundary; backend role checks are.
