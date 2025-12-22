from fastapi import FastAPI, APIRouter, HTTPException, Request, Header, Depends
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ.get('JWT_SECRET')
SUBSCRIPTION_PRICE = float(os.environ.get('SUBSCRIPTION_PRICE', '99.99'))

app = FastAPI()

# Add CORS middleware before defining routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization.split(' ')[1]
    payload = verify_token(token)
    user = await db.users.find_one({'id': payload['user_id']}, {'_id': 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

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


class CreateRentalRequest(BaseModel):
    gear_id: str
    quantity: int
    status: str = 'pending'


class ExtendRentalRequest(BaseModel):
    extension_hours: int = 1


class ReturnRentalRequest(BaseModel):
    pass


class CreateBookingRequest(BaseModel):
    date: str
    slots: List[str]
    type: str
    status: str = 'pending'


class CancelBookingRequest(BaseModel):
    pass

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

@api_router.post("/auth/register")
async def register(req: RegisterRequest):
    existing = await db.users.find_one(
        {'$or': [{'email': req.email}, {'phone': req.phone}]},
        {'_id': 0}
    )
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user_id = str(uuid.uuid4())
    hashed_password = bcrypt.hashpw(req.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user = {
        'id': user_id,
        'name': req.name,
        'email': req.email,
        'phone': req.phone,
        'password': hashed_password,
        'role': 'student',
        'status': 'pending',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user)
    await db.activity_logs.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'action': 'user_registered',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return {'message': 'Registration successful. Please upload ID for verification.', 'user_id': user_id}

@api_router.post("/auth/login")
async def login(req: LoginRequest):
    query = {}
    if req.email:
        query['email'] = req.email
    elif req.phone:
        query['phone'] = req.phone
    else:
        raise HTTPException(status_code=400, detail="Email or phone required")
    
    user = await db.users.find_one(query, {'_id': 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not bcrypt.checkpw(req.password.encode('utf-8'), user['password'].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user['id'], user['email'], user['role'])
    
    return {
        'token': token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'status': user['status']
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

@api_router.get("/turf/availability")
async def get_turf_availability(date: str, current_user: dict = Depends(get_current_user)):
    slots = []
    for hour in range(6, 22):
        slot_time = f"{hour:02d}:00"
        # Check for any existing bookings (confirmed, approved, or pending)
        booking = await db.turf_bookings.find_one(
            {'date': date, 'slot_time': slot_time, 'status': {'$in': ['confirmed', 'approved', 'pending']}},
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


@api_router.get("/bookings/user")
async def get_user_bookings(current_user: dict = Depends(get_current_user)):
    bookings = await db.turf_bookings.find(
        {'user_id': current_user['id']},
        {'_id': 0}
    ).sort('date', -1).to_list(100)
    
    return {'bookings': bookings}


@api_router.post("/bookings/create")
async def create_booking(req: CreateBookingRequest, current_user: dict = Depends(get_current_user)):
    # Check if user already has a booking for any of the requested dates
    for slot in req.slots:
        existing_booking = await db.turf_bookings.find_one({
            'user_id': current_user['id'],
            'date': req.date,
            'status': {'$in': ['pending', 'approved', 'confirmed']}
        })
        
        if existing_booking:
            raise HTTPException(status_code=400, detail="You can only book 1 turf per day. You already have a booking for this date.")
    
    # Create booking records
    booking_records = []
    for slot in req.slots:
        # Check if slot is already booked
        slot_taken = await db.turf_bookings.find_one({
            'date': req.date,
            'slot_time': slot,
            'status': 'confirmed'
        })
        
        if slot_taken:
            raise HTTPException(status_code=400, detail=f"Slot {slot} is already booked")
        
        booking_id = str(uuid.uuid4())
        qr_data = f"turf:{booking_id}:{current_user['id']}:{req.date}:{slot}"
        
        booking = {
            'id': booking_id,
            'user_id': current_user['id'],
            'date': req.date,
            'slot_time': slot,
            'type': req.type,
            'status': req.status,  # 'pending', 'approved', 'confirmed', 'cancelled'
            'qr_code': generate_qr_code(qr_data),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        await db.turf_bookings.insert_one(booking)
        booking_records.append(booking)
    
    # Log activity
    await db.activity_logs.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'action': 'booking_created',
        'details': f"Date: {req.date}, Slots: {', '.join(req.slots)}",
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return {'message': 'Booking request submitted successfully. Waiting for admin approval.', 'bookings': booking_records}


@api_router.post("/bookings/{booking_id}/cancel")
async def cancel_booking(booking_id: str, req: CancelBookingRequest, current_user: dict = Depends(get_current_user)):
    # Find the booking
    booking = await db.turf_bookings.find_one({'id': booking_id, 'user_id': current_user['id']})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Only allow cancellation for pending or approved bookings
    if booking['status'] not in ['pending', 'approved']:
        raise HTTPException(status_code=400, detail="Cannot cancel booking in current status")
    
    # Update booking status to cancelled
    await db.turf_bookings.update_one(
        {'id': booking_id},
        {'$set': {'status': 'cancelled', 'cancelled_at': datetime.now(timezone.utc).isoformat()}}
    )
    
    # Log activity
    await db.activity_logs.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'action': 'booking_cancelled',
        'details': f"Booking ID: {booking_id}",
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return {'message': 'Booking cancelled successfully'}

@api_router.get("/gear/list")
async def get_gear_list(current_user: dict = Depends(get_current_user)):
    gear_items = await db.gear_items.find(
        {'status': 'available'},
        {'_id': 0}
    ).to_list(100)
    
    return {'gear': gear_items}

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


@api_router.post("/rentals/create")
async def create_rental(req: CreateRentalRequest, current_user: dict = Depends(get_current_user)):
    # Check if gear exists and has stock
    gear = await db.gear_items.find_one({'id': req.gear_id})
    if not gear:
        raise HTTPException(status_code=404, detail="Gear not found")
    
    if gear['stock'] < req.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Create rental record
    rental_id = str(uuid.uuid4())
    rental = {
        'id': rental_id,
        'user_id': current_user['id'],
        'gear_id': req.gear_id,
        'quantity': req.quantity,
        'status': req.status,  # 'pending', 'approved', 'active', 'returned', 'overdue'
        'created_at': datetime.now(timezone.utc).isoformat(),
        'due_time': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    }
    
    # Create a copy for the response before inserting to avoid MongoDB modifying the original
    rental_response = rental.copy()
    
    await db.gear_rentals.insert_one(rental)
    
    # Log activity
    await db.activity_logs.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'action': 'rental_created',
        'details': f"Gear: {gear['name']}, Quantity: {req.quantity}",
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return {'message': 'Rental request submitted successfully', 'rental': rental_response}


@api_router.post("/rentals/{rental_id}/extend")
async def extend_rental(rental_id: str, req: ExtendRentalRequest, current_user: dict = Depends(get_current_user)):
    # Find the rental
    rental = await db.gear_rentals.find_one({'id': rental_id, 'user_id': current_user['id']})
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    # Only allow extension for active rentals
    if rental['status'] != 'active':
        raise HTTPException(status_code=400, detail="Can only extend active rentals")
    
    # Update due time
    current_due = datetime.fromisoformat(rental['due_time'])
    new_due = current_due + timedelta(hours=req.extension_hours)
    
    await db.gear_rentals.update_one(
        {'id': rental_id},
        {'$set': {'due_time': new_due.isoformat()}}
    )
    
    # Log activity
    await db.activity_logs.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'action': 'rental_extended',
        'details': f"Rental ID: {rental_id}, Extended by {req.extension_hours} hours",
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return {'message': f'Rental extended by {req.extension_hours} hours'}


@api_router.post("/rentals/{rental_id}/return")
async def return_rental(rental_id: str, req: ReturnRentalRequest, current_user: dict = Depends(get_current_user)):
    # Find the rental
    rental = await db.gear_rentals.find_one({'id': rental_id, 'user_id': current_user['id']})
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    # Update rental status to returned
    await db.gear_rentals.update_one(
        {'id': rental_id},
        {'$set': {'status': 'returned', 'returned_at': datetime.now(timezone.utc).isoformat()}}
    )
    
    # Increase gear stock back
    await db.gear_items.update_one(
        {'id': rental['gear_id']},
        {'$inc': {'stock': rental['quantity']}}
    )
    
    # Log activity
    await db.activity_logs.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'action': 'rental_returned',
        'details': f"Rental ID: {rental_id}",
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return {'message': 'Rental returned successfully'}

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
        {'status': {'$in': ['pending', 'pending_approval']}},
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
    
    # Create the gear object
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
    
    # Insert into database
    await db.gear_items.insert_one(gear)
    
    # Create response object without the MongoDB _id field
    gear_response = {
        'id': gear['id'],
        'name': gear['name'],
        'description': gear['description'],
        'price_per_hour': gear['price_per_hour'],
        'stock': gear['stock'],
        'image_url': gear['image_url'],
        'status': gear['status'],
        'created_at': gear['created_at']
    }
    
    return {'message': 'Gear added successfully', 'gear': gear_response}

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

@api_router.delete("/admin/gear/{gear_id}")
async def delete_gear(gear_id: str, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if gear exists
    gear = await db.gear_items.find_one({'id': gear_id}, {'_id': 0})
    if not gear:
        raise HTTPException(status_code=404, detail="Gear not found")
    
    # Delete the gear item
    result = await db.gear_items.delete_one({'id': gear_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Gear not found")
    
    return {'message': 'Gear deleted successfully'}

@api_router.delete("/admin/rentals/{rental_id}")
async def delete_rental(rental_id: str, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if rental exists
    rental = await db.gear_rentals.find_one({'id': rental_id}, {'_id': 0})
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    # Delete the rental
    result = await db.gear_rentals.delete_one({'id': rental_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    return {'message': 'Rental deleted successfully'}

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
    pending_approvals = await db.users.count_documents({'status': {'$in': ['pending', 'pending_approval']}})
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

@api_router.post("/admin/create")
async def create_admin():
    existing_admin = await db.users.find_one({'email': 'admin@college.edu'}, {'_id': 0})
    if existing_admin:
        return {'message': 'Admin already exists'}
    
    admin_id = str(uuid.uuid4())
    hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    admin = {
        'id': admin_id,
        'name': 'Admin',
        'email': 'admin@college.edu',
        'phone': '1234567890',
        'password': hashed_password,
        'role': 'admin',
        'status': 'approved',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(admin)
    return {'message': 'Admin created', 'email': 'admin@college.edu', 'password': 'admin123'}


@api_router.get("/admin/pending-bookings")
async def get_pending_bookings(current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    pending_bookings = await db.turf_bookings.find(
        {'status': 'pending'},
        {'_id': 0}
    ).sort('created_at', -1).to_list(100)
    
    # Add user details to each booking
    for booking in pending_bookings:
        user = await db.users.find_one({'id': booking['user_id']}, {'_id': 0, 'password': 0})
        booking['user'] = user
    
    return {'pending_bookings': pending_bookings}


@api_router.get("/admin/pending-rentals")
async def get_pending_rentals(current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    pending_rentals = await db.gear_rentals.find(
        {'status': 'pending'},
        {'_id': 0}
    ).sort('created_at', -1).to_list(100)
    
    # Add user and gear details to each rental
    for rental in pending_rentals:
        user = await db.users.find_one({'id': rental['user_id']}, {'_id': 0, 'password': 0})
        gear = await db.gear_items.find_one({'id': rental['gear_id']}, {'_id': 0})
        rental['user'] = user
        rental['gear'] = gear
    
    return {'pending_rentals': pending_rentals}


@api_router.post("/admin/approve-booking/{booking_id}")
async def approve_booking(booking_id: str, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Find the booking
    booking = await db.turf_bookings.find_one({'id': booking_id})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Update booking status to confirmed
    await db.turf_bookings.update_one(
        {'id': booking_id},
        {'$set': {'status': 'confirmed'}}
    )
    
    # Log activity
    await db.activity_logs.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'action': 'booking_approved',
        'details': f"Booking ID: {booking_id}",
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return {'message': 'Booking approved successfully'}


@api_router.post("/admin/reject-booking/{booking_id}")
async def reject_booking(booking_id: str, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Find the booking
    booking = await db.turf_bookings.find_one({'id': booking_id})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Update booking status to rejected
    await db.turf_bookings.update_one(
        {'id': booking_id},
        {'$set': {'status': 'rejected'}}
    )
    
    # Log activity
    await db.activity_logs.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'action': 'booking_rejected',
        'details': f"Booking ID: {booking_id}",
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return {'message': 'Booking rejected successfully'}


@api_router.post("/admin/approve-rental/{rental_id}")
async def approve_rental(rental_id: str, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Find the rental
    rental = await db.gear_rentals.find_one({'id': rental_id})
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    # Check if gear has sufficient stock
    gear = await db.gear_items.find_one({'id': rental['gear_id']})
    if not gear or gear['stock'] < rental['quantity']:
        raise HTTPException(status_code=400, detail="Insufficient gear stock")
    
    # Update rental status to active
    await db.gear_rentals.update_one(
        {'id': rental_id},
        {'$set': {'status': 'active'}}
    )
    
    # Reduce gear stock
    await db.gear_items.update_one(
        {'id': rental['gear_id']},
        {'$inc': {'stock': -rental['quantity']}}
    )
    
    # Log activity
    await db.activity_logs.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'action': 'rental_approved',
        'details': f"Rental ID: {rental_id}",
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return {'message': 'Rental approved successfully'}


@api_router.post("/admin/reject-rental/{rental_id}")
async def reject_rental(rental_id: str, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Find the rental
    rental = await db.gear_rentals.find_one({'id': rental_id})
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    # Update rental status to rejected
    await db.gear_rentals.update_one(
        {'id': rental_id},
        {'$set': {'status': 'rejected'}}
    )
    
    # Log activity
    await db.activity_logs.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'action': 'rental_rejected',
        'details': f"Rental ID: {rental_id}",
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return {'message': 'Rental rejected successfully'}

app.include_router(api_router)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()