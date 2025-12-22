from fastapi import FastAPI, APIRouter, HTTPException, Request, Header, Depends
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import AsyncSession
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import qrcode
import io
import base64
# Removed import for emergentintegrations
# Using mock classes instead

from db_pg import get_async_session
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, select, and_, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="student")
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class DigitalID(Base):
    __tablename__ = "digital_ids"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    qr_code_url = Column(Text)
    issued_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True))

class CheckoutSessionRequest:
    def __init__(self, amount, currency, success_url, cancel_url, metadata=None):
        self.amount = amount
        self.currency = currency
        self.success_url = success_url
        self.cancel_url = cancel_url
        self.metadata = metadata or {}

class CheckoutStatusResponse:
    def __init__(self, status, payment_status):
        self.status = status
        self.payment_status = payment_status

class CheckoutSessionResponse:
    def __init__(self, session_id, url):
        self.session_id = session_id
        self.url = url

class MockStripeCheckout:
    def __init__(self, api_key=None, webhook_url=None):
        self.api_key = api_key
        self.webhook_url = webhook_url
    
    async def create_checkout_session(self, request):
        # Mock implementation
        return CheckoutSessionResponse(str(uuid.uuid4()), 'http://localhost:8001/mock-checkout')
    
    async def get_checkout_status(self, session_id):
        # Mock implementation
        return CheckoutStatusResponse('complete', 'paid')
    
    async def handle_webhook(self, body, signature):
        # Mock implementation
        return {'status': 'success'}

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
JWT_SECRET = os.environ.get('JWT_SECRET')
SUBSCRIPTION_PRICE = float(os.environ.get('SUBSCRIPTION_PRICE', '99.99'))

app = FastAPI()
api_router = APIRouter(prefix="/api")

def generate_qr_code(data: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def create_token(user_id: str, email: str, role: str) -> str:
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.now(timezone.utc) + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(authorization: str = Header(None), session: AsyncSession = Depends(get_async_session)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization.split(' ')[1]
    payload = verify_token(token)
    result = await session.execute(select(User).where(User.id == payload['user_id']))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Return a dict to match existing API contract used by other endpoints
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "status": "approved" if user.is_approved else "pending"
    }

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str

class LoginRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str

class IDUploadRequest(BaseModel):
    id_image_url: str
    student_id: str

class TurfBookingRequest(BaseModel):
    date: str
    slot_time: str

class GearRentalRequest(BaseModel):
    gear_id: str
    quantity: int

class AdminApprovalRequest(BaseModel):
    user_id: str
    action: str

class GearItemRequest(BaseModel):
    name: str
    description: str
    price_per_hour: float
    stock: int
    image_url: Optional[str] = None

class TurfSlotRequest(BaseModel):
    date: str
    slot_time: str
    status: str

class RegisterModel(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

@api_router.post("/api/register", response_model=dict)
async def register(user: RegisterModel, session: AsyncSession = Depends(get_async_session)):
    """Register a new user (student or admin)."""
    try:
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.email == user.email)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create new user
        new_user = User(
            name=user.name,
            email=user.email,
            password=hashed_password,
            role=user.role,
            is_approved=(user.role == "admin")  # Auto-approve admins
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        
        return {
            "message": "User registered successfully",
            "userId": str(new_user.id),
            "role": new_user.role,
            "isApproved": new_user.is_approved
        }
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@api_router.post("/auth/login")
async def login(req: LoginRequest, session: AsyncSession = Depends(get_async_session)):
    if req.email:
        query = User.email == req.email
    elif req.phone:
        # For now, we only support email login; phone numbers would require an additional column
        raise HTTPException(status_code=400, detail="Email login only supported")
    else:
        raise HTTPException(status_code=400, detail="Email or phone required")
    
    result = await session.execute(select(User).where(query))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not bcrypt.checkpw(req.password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(str(user.id), user.email, user.role)
    
    return {
        'token': token,
        'user': {
            'id': str(user.id),
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'status': 'approved' if user.is_approved else 'pending'
        }
    }

@api_router.post("/student/upload-id")
async def upload_id(req: IDUploadRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    digital_id = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'student_id': req.student_id,
        'id_image_url': req.id_image_url,
        'qr_code': generate_qr_code(f"student:{user_id}"),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.digital_ids.insert_one(digital_id)
    await db.users.update_one(
        {'id': user_id},
        {'$set': {'status': 'pending_approval'}}
    )
    
    await db.activity_logs.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'action': 'id_uploaded',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return {'message': 'ID uploaded successfully. Awaiting admin approval.'}

@api_router.get("/student/status")
async def get_student_status(current_user: dict = Depends(get_current_user)):
    subscription = await db.subscriptions.find_one(
        {'user_id': current_user['id'], 'status': 'active'},
        {'_id': 0}
    )
    
    return {
        'user_status': current_user['status'],
        'has_active_subscription': subscription is not None,
        'subscription': subscription
    }

@api_router.post("/subscription/create-checkout")
async def create_subscription_checkout(request: Request, current_user: dict = Depends(get_current_user)):
    body = await request.json()
    origin_url = body.get('origin_url')
    
    if not origin_url:
        raise HTTPException(status_code=400, detail="origin_url required")
    
    host_url = origin_url
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = MockStripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    success_url = f"{origin_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/subscription-payment"
    
    checkout_request = CheckoutSessionRequest(
        amount=SUBSCRIPTION_PRICE,
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'user_id': current_user['id'],
            'type': 'subscription'
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    await db.payment_transactions.insert_one({
        'id': str(uuid.uuid4()),
        'session_id': session.session_id,
        'user_id': current_user['id'],
        'amount': SUBSCRIPTION_PRICE,
        'currency': 'usd',
        'type': 'subscription',
        'payment_status': 'pending',
        'created_at': datetime.now(timezone.utc).isoformat()
    })
    
    return {'url': session.url, 'session_id': session.session_id}

@api_router.get("/subscription/checkout-status/{session_id}")
async def get_subscription_checkout_status(session_id: str, current_user: dict = Depends(get_current_user)):
    transaction = await db.payment_transactions.find_one({'session_id': session_id}, {'_id': 0})
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction.get('payment_status') == 'paid':
        return {'status': 'completed', 'payment_status': 'paid'}
    
    host_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = MockStripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    checkout_status = await stripe_checkout.get_checkout_status(session_id)
    
    if checkout_status.payment_status == 'paid' and transaction.get('payment_status') != 'paid':
        await db.payment_transactions.update_one(
            {'session_id': session_id},
            {'$set': {'payment_status': 'paid', 'updated_at': datetime.now(timezone.utc).isoformat()}}
        )
        
        subscription = {
            'id': str(uuid.uuid4()),
            'user_id': current_user['id'],
            'start_date': datetime.now(timezone.utc).isoformat(),
            'end_date': (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
            'status': 'active',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.subscriptions.insert_one(subscription)
        
        await db.activity_logs.insert_one({
            'id': str(uuid.uuid4()),
            'user_id': current_user['id'],
            'action': 'subscription_activated',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    return {
        'status': checkout_status.status,
        'payment_status': checkout_status.payment_status
    }

@api_router.get("/turf/availability")
async def get_turf_availability(date: str, current_user: dict = Depends(get_current_user)):
    slots = []
    for hour in range(6, 22):
        slot_time = f"{hour:02d}:00"
        booking = await db.turf_bookings.find_one(
            {'date': date, 'slot_time': slot_time, 'status': 'confirmed'},
            {'_id': 0}
        )
        slots.append({
            'time': slot_time,
            'available': booking is None
        })
    
    return {'date': date, 'slots': slots}

@api_router.post("/turf/book")
async def book_turf(req: TurfBookingRequest, current_user: dict = Depends(get_current_user)):
    booking_date = datetime.fromisoformat(req.date)
    today = datetime.now(timezone.utc).date()
    tomorrow = today + timedelta(days=1)
    
    if booking_date.date() != tomorrow:
        raise HTTPException(status_code=400, detail="Bookings only allowed for tomorrow")
    
    existing_today = await db.turf_bookings.find_one(
        {
            'user_id': current_user['id'],
            'date': req.date,
            'status': 'confirmed'
        },
        {'_id': 0}
    )
    
    if existing_today:
        raise HTTPException(status_code=400, detail="Daily booking limit reached")
    
    slot_taken = await db.turf_bookings.find_one(
        {'date': req.date, 'slot_time': req.slot_time, 'status': 'confirmed'},
        {'_id': 0}
    )
    
    if slot_taken:
        raise HTTPException(status_code=400, detail="Slot already booked")
    
    booking_id = str(uuid.uuid4())
    qr_data = f"turf:{booking_id}:{current_user['id']}:{req.date}:{req.slot_time}"
    
    booking = {
        'id': booking_id,
        'user_id': current_user['id'],
        'date': req.date,
        'slot_time': req.slot_time,
        'status': 'confirmed',
        'qr_code': generate_qr_code(qr_data),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.turf_bookings.insert_one(booking)
    
    await db.activity_logs.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'action': 'turf_booked',
        'details': f"Date: {req.date}, Slot: {req.slot_time}",
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return {'message': 'Turf booked successfully', 'booking': booking}

@api_router.get("/turf/my-bookings")
async def get_my_bookings(current_user: dict = Depends(get_current_user)):
    bookings = await db.turf_bookings.find(
        {'user_id': current_user['id']},
        {'_id': 0}
    ).sort('date', -1).to_list(100)
    
    return {'bookings': bookings}

@api_router.get("/gear/list")
async def get_gear_list(current_user: dict = Depends(get_current_user)):
    gear_items = await db.gear_items.find(
        {'status': 'available'},
        {'_id': 0}
    ).to_list(100)
    
    return {'gear': gear_items}

@api_router.post("/gear/rent-checkout")
async def create_gear_rental_checkout(request: Request, req: GearRentalRequest, current_user: dict = Depends(get_current_user)):
    body = await request.json()
    origin_url = body.get('origin_url')
    
    if not origin_url:
        raise HTTPException(status_code=400, detail="origin_url required")
    
    gear = await db.gear_items.find_one({'id': req.gear_id}, {'_id': 0})
    if not gear:
        raise HTTPException(status_code=404, detail="Gear not found")
    
    if gear['stock'] < req.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    amount = gear['price_per_hour'] * req.quantity
    
    host_url = origin_url
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = MockStripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    success_url = f"{origin_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/gear-rental"
    
    checkout_request = CheckoutSessionRequest(
        amount=amount,
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'user_id': current_user['id'],
            'type': 'gear_rental',
            'gear_id': req.gear_id,
            'quantity': str(req.quantity)
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    await db.payment_transactions.insert_one({
        'id': str(uuid.uuid4()),
        'session_id': session.session_id,
        'user_id': current_user['id'],
        'amount': amount,
        'currency': 'usd',
        'type': 'gear_rental',
        'gear_id': req.gear_id,
        'quantity': req.quantity,
        'payment_status': 'pending',
        'created_at': datetime.now(timezone.utc).isoformat()
    })
    
    return {'url': session.url, 'session_id': session.session_id}

@api_router.get("/gear/checkout-status/{session_id}")
async def get_gear_checkout_status(session_id: str, current_user: dict = Depends(get_current_user)):
    transaction = await db.payment_transactions.find_one({'session_id': session_id}, {'_id': 0})
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction.get('payment_status') == 'paid':
        return {'status': 'completed', 'payment_status': 'paid'}
    
    host_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = MockStripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    checkout_status = await stripe_checkout.get_checkout_status(session_id)
    
    if checkout_status.payment_status == 'paid' and transaction.get('payment_status') != 'paid':
        await db.payment_transactions.update_one(
            {'session_id': session_id},
            {'$set': {'payment_status': 'paid', 'updated_at': datetime.now(timezone.utc).isoformat()}}
        )
        
        rental_id = str(uuid.uuid4())
        qr_data = f"gear:{rental_id}:{current_user['id']}:{transaction['gear_id']}"
        
        rental = {
            'id': rental_id,
            'user_id': current_user['id'],
            'gear_id': transaction['gear_id'],
            'quantity': transaction['quantity'],
            'rental_start': datetime.now(timezone.utc).isoformat(),
            'rental_end': None,
            'status': 'active',
            'qr_code': generate_qr_code(qr_data),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.gear_rentals.insert_one(rental)
        
        await db.gear_items.update_one(
            {'id': transaction['gear_id']},
            {'$inc': {'stock': -transaction['quantity']}}
        )
    
    return {
        'status': checkout_status.status,
        'payment_status': checkout_status.payment_status
    }

@api_router.get("/gear/my-rentals")
async def get_my_rentals(current_user: dict = Depends(get_current_user)):
    rentals = await db.gear_rentals.find(
        {'user_id': current_user['id']},
        {'_id': 0}
    ).sort('created_at', -1).to_list(100)
    
    for rental in rentals:
        gear = await db.gear_items.find_one({'id': rental['gear_id']}, {'_id': 0})
        rental['gear_name'] = gear['name'] if gear else 'Unknown'
    
    return {'rentals': rentals}

@api_router.get("/student/digital-id")
async def get_digital_id(current_user: dict = Depends(get_current_user)):
    digital_id = await db.digital_ids.find_one(
        {'user_id': current_user['id']},
        {'_id': 0}
    )
    
    if not digital_id:
        raise HTTPException(status_code=404, detail="Digital ID not found")
    
    return digital_id

@api_router.get("/admin/pending-students")
async def get_pending_students(current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    pending_users = await db.users.find(
        {'status': 'pending_approval'},
        {'_id': 0, 'password': 0}
    ).to_list(100)
    
    for user in pending_users:
        digital_id = await db.digital_ids.find_one({'user_id': user['id']}, {'_id': 0})
        user['digital_id'] = digital_id
    
    return {'pending_students': pending_users}

@api_router.post("/admin/approve-student")
async def approve_student(req: AdminApprovalRequest, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if req.action not in ['approve', 'reject']:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    new_status = 'approved' if req.action == 'approve' else 'rejected'
    
    await db.users.update_one(
        {'id': req.user_id},
        {'$set': {'status': new_status}}
    )
    
    await db.activity_logs.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'action': f'student_{req.action}d',
        'details': f"Student {req.user_id}",
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return {'message': f'Student {req.action}d successfully'}

@api_router.get("/admin/gear")
async def get_admin_gear(current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    gear_items = await db.gear_items.find({}, {'_id': 0}).to_list(1000)
    return {'gear': gear_items}

@api_router.post("/admin/gear")
async def add_gear(req: GearItemRequest, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    gear = {
        'id': str(uuid.uuid4()),
        'name': req.name,
        'description': req.description,
        'price_per_hour': req.price_per_hour,
        'stock': req.stock,
        'image_url': req.image_url,
        'status': 'available',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.gear_items.insert_one(gear)
    return {'message': 'Gear added successfully', 'gear': gear}

@api_router.put("/admin/gear/{gear_id}")
async def update_gear(gear_id: str, req: GearItemRequest, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    await db.gear_items.update_one(
        {'id': gear_id},
        {'$set': {
            'name': req.name,
            'description': req.description,
            'price_per_hour': req.price_per_hour,
            'stock': req.stock,
            'image_url': req.image_url
        }}
    )
    
    return {'message': 'Gear updated successfully'}

@api_router.get("/admin/turf-slots")
async def get_admin_turf_slots(date: str, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    bookings = await db.turf_bookings.find({'date': date}, {'_id': 0}).to_list(100)
    return {'bookings': bookings}

@api_router.get("/admin/reports")
async def get_admin_reports(current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total_users = await db.users.count_documents({})
    pending_approvals = await db.users.count_documents({'status': 'pending_approval'})
    active_subscriptions = await db.subscriptions.count_documents({'status': 'active'})
    total_bookings = await db.turf_bookings.count_documents({})
    total_rentals = await db.gear_rentals.count_documents({})
    
    return {
        'total_users': total_users,
        'pending_approvals': pending_approvals,
        'active_subscriptions': active_subscriptions,
        'total_bookings': total_bookings,
        'total_rentals': total_rentals
    }

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    host_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = MockStripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        return {'received': True}
    except Exception as e:
        logging.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail="Webhook error")

@api_router.post("/admin/create")
async def create_admin(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(User).where(User.email == 'admin@college.edu'))
    existing_admin = result.scalar_one_or_none()
    if existing_admin:
        return {'message': 'Admin already exists'}
    
    hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    admin = User(
        name='Admin',
        email='admin@college.edu',
        password=hashed_password,
        role='admin',
        is_approved=True
    )
    session.add(admin)
    await session.commit()
    
    return {'message': 'Admin created', 'email': 'admin@college.edu', 'password': 'admin123'}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()