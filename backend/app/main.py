import os, json, uuid
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from .database import Base, engine, get_db
from .models import User, Product, Order, Prescription
from .schemas import RegisterIn, LoginIn, ProductIn, OrderIn, StatusIn
from .security import hash_password, verify_password, create_token, current_user, admin_user

Base.metadata.create_all(bind=engine)

def init_default_data():
    from .database import SessionLocal
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.role == "admin").first():
            admins = [
                ("admin@vaidhya.com", "Admin@123456"),
                ("admin@vaidhya-pharmacy.com", "Vaidhya@Admin2024!"),
            ]
            for em, pw in admins:
                if not db.query(User).filter(User.email == em.lower()).first():
                    db.add(User(name="Vaidhya Admin", email=em.lower(), password_hash=hash_password(pw), role="admin"))
            db.commit()

        if not db.query(Product).first():
            samples = [
                dict(name='Vitamin C 500mg', category='Vitamins', description='Sample catalogue item. Verify product details and regulatory requirements before sale.', price=180, stock=40, image_url='https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=500', prescription_required=False),
                dict(name='Digital Thermometer', category='Health Devices', description='Easy-to-read digital thermometer.', price=249, stock=25, image_url='https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=500', prescription_required=False),
                dict(name='Gentle Skin Care Lotion', category='Personal Care', description='Gentle daily skin care product.', price=320, stock=18, image_url='https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=500', prescription_required=False),
                dict(name='Baby Care Essentials', category='Baby Care', description='Sample baby-care catalogue item.', price=150, stock=20, image_url='https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500', prescription_required=False),
            ]
            for item in samples:
                db.add(Product(**item))
            db.commit()
    except Exception:
        pass
    finally:
        db.close()

init_default_data()

app = FastAPI(title="Vaidhya Pharmacy API", version="1.0.0")
origins = [o.strip() for o in os.getenv("FRONTEND_ORIGIN", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins,
                   allow_origin_regex=r"^(https?://(localhost|127\.0\.0\.1)(:[0-9]+)?|https://.*\.vercel\.app)$",
                   allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

def user_out(u):
    return {"id": u.id, "name": u.name, "email": u.email, "phone": u.phone, "role": u.role}

def product_out(p):
    return {"id": p.id, "name": p.name, "category": p.category, "description": p.description,
            "price": p.price, "stock": p.stock, "prescription_required": p.prescription_required,
            "image_url": p.image_url}

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Vaidhya Pharmacy API"}

@app.post("/api/auth/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(User).filter(func.lower(User.email) == email).first():
        raise HTTPException(409, "An account with this email already exists")
    u = User(name=data.name, email=email, phone=data.phone,
             password_hash=hash_password(data.password), role="customer")
    db.add(u); db.commit(); db.refresh(u)
    return {"access_token": create_token(u), "token_type": "bearer", "user": user_out(u)}

@app.post("/api/auth/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    u = db.query(User).filter(func.lower(User.email) == data.email.lower()).first()
    if not u or not verify_password(data.password, u.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return {"access_token": create_token(u), "token_type": "bearer", "user": user_out(u)}

@app.get("/api/auth/me")
def me(user: User = Depends(current_user)):
    return user_out(user)

@app.get("/api/products")
def products(q: str = "", category: str = "", db: Session = Depends(get_db)):
    query = db.query(Product).filter(Product.active == True)
    if q: query = query.filter(Product.name.ilike(f"%{q}%"))
    if category: query = query.filter(Product.category == category)
    return [product_out(p) for p in query.order_by(Product.name).all()]

@app.post("/api/orders")
def create_order(data: OrderIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not data.items: raise HTTPException(400, "Your cart is empty")
    rows, total, prescription_needed = [], 0, False
    for item in data.items:
        p = db.get(Product, item.product_id)
        if not p or not p.active: raise HTTPException(404, f"Product {item.product_id} unavailable")
        if p.stock < item.quantity: raise HTTPException(400, f"Insufficient stock for {p.name}")
        prescription_needed = prescription_needed or p.prescription_required
        rows.append({"product_id": p.id, "name": p.name, "quantity": item.quantity, "unit_price": p.price})
        total += p.price * item.quantity
    if prescription_needed and not data.prescription_id:
        raise HTTPException(400, "A prescription must be uploaded for this order")
    prescription = db.get(Prescription, data.prescription_id) if data.prescription_id else None
    if prescription and prescription.user_id != user.id:
        raise HTTPException(403, "Invalid prescription")
    order = Order(user_id=user.id, items_json=json.dumps(rows), total=round(total,2),
                  address=data.address, payment_method=data.payment_method,
                  prescription_path=str(prescription.id) if prescription else None,
                  status="Awaiting pharmacist review" if prescription_needed else "Pending")
    for item in data.items:
        db.get(Product, item.product_id).stock -= item.quantity
    db.add(order); db.commit(); db.refresh(order)
    return {"id": order.id, "total": order.total, "status": order.status}

@app.get("/api/orders/mine")
def my_orders(user: User = Depends(current_user), db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).all()
    return [{"id": o.id, "items": json.loads(o.items_json), "total": o.total,
             "address": o.address, "payment_method": o.payment_method,
             "status": o.status, "created_at": o.created_at.isoformat()} for o in orders]

@app.post("/api/prescriptions")
async def upload_prescription(file: UploadFile = File(...), user: User = Depends(current_user),
                              db: Session = Depends(get_db)):
    allowed = {".pdf", ".jpg", ".jpeg", ".png"}
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed: raise HTTPException(400, "Only PDF, JPG and PNG files are accepted")
    max_bytes = int(os.getenv("MAX_UPLOAD_MB", "5")) * 1024 * 1024
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes: raise HTTPException(413, "File is larger than the upload limit")
    default_upload = "/tmp/private_uploads" if os.getenv("VERCEL") else "./private_uploads"
    folder = Path(os.getenv("UPLOAD_DIR", default_upload))
    folder.mkdir(parents=True, exist_ok=True)
    stored = f"{uuid.uuid4().hex}{suffix}"
    (folder / stored).write_bytes(content)
    rec = Prescription(user_id=user.id, stored_name=stored, original_name=file.filename or stored)
    db.add(rec); db.commit(); db.refresh(rec)
    return {"id": rec.id, "status": rec.status, "filename": rec.original_name}

@app.get("/api/admin/summary")
def admin_summary(_: User = Depends(admin_user), db: Session = Depends(get_db)):
    return {"orders": db.query(Order).count(), "customers": db.query(User).filter(User.role=="customer").count(),
            "products": db.query(Product).count(), "low_stock": db.query(Product).filter(Product.stock < 10).count(),
            "sales": round(db.query(func.sum(Order.total)).scalar() or 0, 2)}

@app.get("/api/admin/orders")
def admin_orders(_: User = Depends(admin_user), db: Session = Depends(get_db)):
    rows = db.query(Order).order_by(Order.created_at.desc()).all()
    return [{"id": o.id, "customer": o.user.name, "email": o.user.email,
             "items": json.loads(o.items_json), "total": o.total, "status": o.status,
             "created_at": o.created_at.isoformat()} for o in rows]

@app.put("/api/admin/orders/{order_id}/status")
def update_order(order_id: int, data: StatusIn, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    allowed = {"Pending", "Processing", "Shipped", "Delivered", "Cancelled",
               "Awaiting pharmacist review", "Rejected"}
    if data.status not in allowed: raise HTTPException(400, "Invalid order status")
    order = db.get(Order, order_id)
    if not order: raise HTTPException(404, "Order not found")
    order.status = data.status; db.commit()
    return {"id": order.id, "status": order.status}

@app.post("/api/admin/products")
def add_product(data: ProductIn, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    p = Product(**data.model_dump()); db.add(p); db.commit(); db.refresh(p)
    return product_out(p)

@app.put("/api/admin/products/{product_id}")
def edit_product(product_id: int, data: ProductIn, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    p = db.get(Product, product_id)
    if not p: raise HTTPException(404, "Product not found")
    for key, value in data.model_dump().items(): setattr(p, key, value)
    db.commit(); db.refresh(p)
    return product_out(p)

@app.delete("/api/admin/products/{product_id}")
def delete_product(product_id: int, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    p = db.get(Product, product_id)
    if not p: raise HTTPException(404, "Product not found")
    p.active = False; db.commit()
    return {"ok": True}


# --- Admin operations: customer records, prescription review and reports ---
from fastapi.responses import FileResponse
from sqlalchemy import desc

@app.get('/api/admin/customers')
def admin_customers(_: User = Depends(admin_user), db: Session = Depends(get_db)):
    users = db.query(User).filter(User.role == 'customer').order_by(desc(User.created_at)).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "phone": u.phone,
             "joined": u.created_at.isoformat(),
             "orders": db.query(Order).filter(Order.user_id == u.id).count()} for u in users]

@app.get('/api/admin/prescriptions')
def admin_prescriptions(_: User = Depends(admin_user), db: Session = Depends(get_db)):
    rows = db.query(Prescription).order_by(desc(Prescription.created_at)).all()
    return [{"id": p.id, "customer": db.get(User, p.user_id).name,
             "customer_email": db.get(User, p.user_id).email,
             "filename": p.original_name, "status": p.status,
             "created_at": p.created_at.isoformat()} for p in rows]

@app.get('/api/admin/prescriptions/{prescription_id}/file')
def admin_prescription_file(prescription_id: int, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    p = db.get(Prescription, prescription_id)
    if not p: raise HTTPException(404, 'Prescription not found')
    default_upload = "/tmp/private_uploads" if os.getenv("VERCEL") else "./private_uploads"
    folder = Path(os.getenv('UPLOAD_DIR', default_upload)).resolve()
    path = (folder / p.stored_name).resolve()
    if folder not in path.parents or not path.is_file(): raise HTTPException(404, 'Prescription file unavailable')
    suffix = path.suffix.lower()
    media = 'application/pdf' if suffix == '.pdf' else ('image/png' if suffix == '.png' else 'image/jpeg')
    return FileResponse(path, media_type=media, filename=p.original_name, headers={'Cache-Control':'no-store'})

@app.put('/api/admin/prescriptions/{prescription_id}/review')
def review_prescription(prescription_id: int, data: StatusIn, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    if data.status not in {'Approved', 'Rejected', 'Pending review'}:
        raise HTTPException(400, 'Status must be Approved, Rejected or Pending review')
    p = db.get(Prescription, prescription_id)
    if not p: raise HTTPException(404, 'Prescription not found')
    p.status = data.status
    # Keep related orders in sync with the pharmacist decision.
    linked = db.query(Order).filter(Order.prescription_path == str(p.id)).all()
    for order in linked:
        if data.status == 'Approved' and order.status == 'Awaiting pharmacist review': order.status = 'Processing'
        elif data.status == 'Rejected': order.status = 'Rejected'
        elif data.status == 'Pending review': order.status = 'Awaiting pharmacist review'
    db.commit()
    return {'id': p.id, 'status': p.status, 'updated_orders': len(linked)}

@app.get('/api/admin/reports')
def admin_reports(_: User = Depends(admin_user), db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(desc(Order.created_at)).all()
    by_status = {}
    for order in orders: by_status[order.status] = by_status.get(order.status, 0) + 1
    return {'total_orders': len(orders), 'gross_order_value': round(sum(o.total for o in orders if o.status != 'Cancelled'), 2),
            'orders_by_status': by_status,
            'low_stock_products': [product_out(p) for p in db.query(Product).filter(Product.active == True, Product.stock < 10).order_by(Product.stock).all()]}

@app.get('/api/admin/products')
def admin_products(_: User = Depends(admin_user), db: Session = Depends(get_db)):
    return [product_out(p) | {'active': p.active} for p in db.query(Product).order_by(Product.name).all()]

# Mount React static frontend SPA
from fastapi.staticfiles import StaticFiles
FRONTEND_DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        return FileResponse(str(FRONTEND_DIST / "index.html"))
