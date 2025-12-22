# College Sports Facility Management System

## Overview

This is a comprehensive sports facility management system designed for college campuses. The application allows students to browse, rent sports equipment, and book turf facilities. Administrators can manage inventory, approve requests, and monitor facility usage.

## Tech Stack

### Frontend
- React.js with JSX
- TailwindCSS for styling
- Responsive design for all device sizes

### Backend
- FastAPI (Python)
- MongoDB for data storage
- JWT for authentication
- Uvicorn as ASGI server

### Database
- MongoDB for flexible document storage

## System Architecture

```
┌─────────────┐    REST API    ┌──────────────┐
│   React     │ ←─────────────→│   FastAPI    │
│  Frontend   │                │   Backend    │
└─────────────┘                └──────────────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │   MongoDB    │
                              │   Database   │
                              └──────────────┘
```

## Features

### For Students
1. **User Authentication**
   - Registration with email/phone
   - Login with credentials
   - Digital ID verification

2. **Equipment Rental**
   - Browse available sports equipment
   - View equipment details (pricing, availability)
   - Rent equipment with quantity selection
   - View rental history
   - Extend or return rentals

3. **Turf Booking**
   - View available time slots
   - Book turf for specific dates/times
   - View booking history
   - Cancel bookings

4. **Profile Management**
   - View account status
   - Upload digital ID for verification

### For Administrators
1. **User Management**
   - Approve/reject student registrations
   - View pending approvals

2. **Equipment Management**
   - Add new equipment
   - Update equipment details
   - Remove equipment from inventory
   - Monitor stock levels

3. **Rental Management**
   - View pending rental requests
   - Approve/reject rental requests
   - Track active rentals

4. **Booking Management**
   - View pending turf bookings
   - Approve/reject bookings
   - Manage turf schedule

5. **Reporting**
   - View facility usage statistics
   - Monitor active subscriptions

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/student/upload-id` - Upload digital ID

### Equipment
- `GET /api/gear/list` - Get available equipment
- `GET /api/gear/my-rentals` - Get user's rental history
- `POST /api/rentals/create` - Create rental request
- `POST /api/rentals/{id}/extend` - Extend rental
- `POST /api/rentals/{id}/return` - Return equipment

### Turf Booking
- `GET /api/turf/availability` - Get turf availability
- `GET /api/turf/my-bookings` - Get user's bookings
- `POST /api/turf/book` - Book turf slot

### Admin Functions
- `GET /api/admin/pending-students` - Get pending student approvals
- `POST /api/admin/approve-student` - Approve/reject students
- `GET /api/admin/gear` - Get all equipment
- `POST /api/admin/gear` - Add new equipment
- `PUT /api/admin/gear/{id}` - Update equipment
- `DELETE /api/admin/gear/{id}` - Delete equipment
- `GET /api/admin/pending-rentals` - Get pending rentals
- `POST /api/admin/approve-rental/{id}` - Approve/reject rentals
- `GET /api/admin/pending-bookings` - Get pending bookings
- `POST /api/admin/approve-booking/{id}` - Approve/reject bookings

## Available Equipment

Below is a list of all equipment available in our sports facility:

### 1. Tennis Equipment
![Tennis Racket](https://images.unsplash.com/photo-1581588667945-13abf4db4a58?w=400&h=300&fit=crop)
- **Tennis Racket - Wilson Pro Staff**
  - Description: Professional grade tennis racket with excellent control and power. Perfect for intermediate to advanced players.
  - Price: ₹50/hr
  - Stock: 8 available

### 2. Basketball Equipment
![Basketball](https://images.unsplash.com/photo-1546519638-68e109498ffc?w=400&h=300&fit=crop)
- **Basketball - Spalding NBA Official**
  - Description: Official size basketball used in NBA games. Premium composite leather construction for superior grip.
  - Price: ₹30/hr
  - Stock: 15 available

![Basketball](https://images.unsplash.com/photo-1546519638-68e109498ffc?w=400&h=300&fit=crop)
- **Basketball**
  - Price: ₹5/hr
  - Stock: 9 available

![Basketball](https://images.unsplash.com/photo-1546519638-68e109498ffc?w=400&h=300&fit=crop)
- **Test Basketball**
  - Description: Official size basketball for testing
  - Price: ₹5/hr
  - Stock: 10 available

### 3. Badminton Equipment
![Badminton Set](https://images.unsplash.com/photo-1579504137364-ef0f3c6a7e2c?w=400&h=300&fit=crop)
- **Badminton Set - Yonex Nanoray**
  - Description: Complete badminton set with lightweight racquets and durable shuttlecocks. Ideal for casual and competitive play.
  - Price: ₹40/hr
  - Stock: 10 available

### 4. Football Equipment
![Football](https://images.unsplash.com/photo-1579504137364-ef0f3c6a7e2c?w=400&h=300&fit=crop)
- **Football - Adidas Predator**
  - Description: High-performance football with excellent touch and durability. Perfect for training and matches.
  - Price: ₹35/hr
  - Stock: 12 available

![Football](https://images.unsplash.com/photo-1579504137364-ef0f3c6a7e2c?w=400&h=300&fit=crop)
- **Football**
  - Price: ₹10/hr
  - Stock: 97 available

### 5. Cricket Equipment
![Cricket Bat](https://images.unsplash.com/photo-1521205050117-aaae1fcac0d5?w=400&h=300&fit=crop)
- **Cricket Bat - SS Kashmir Willow**
  - Description: Premium cricket bat made from selected Kashmir willow. Excellent pick-up and powerful shots.
  - Price: ₹60/hr
  - Stock: 6 available

### 6. Volleyball Equipment
![Volleyball](https://images.unsplash.com/photo-1581588667945-13abf4db4a58?w=400&h=300&fit=crop)
- **Volleyball - Mikasa MVA200**
  - Description: Official tournament volleyball with superior grip and durability. Used in international competitions.
  - Price: ₹25/hr
  - Stock: 10 available

### 7. Swimming Equipment
![Swimming Goggles](https://images.unsplash.com/photo-1530543787849-128d94430c6b?w=400&h=300&fit=crop)
- **Swimming Goggles - Speedo Fastskin**
  - Description: Advanced swimming goggles with anti-fog coating and comfortable silicone seal. Perfect for training and competition.
  - Price: ₹20/hr
  - Stock: 20 available

### 8. Gym Equipment
![Gym Towels](https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=400&h=300&fit=crop)
- **Gym Towels - Microfiber Set**
  - Description: Set of 3 premium microfiber towels perfect for gym workouts. Highly absorbent and quick-drying.
  - Price: ₹15/hr
  - Stock: 25 available

### 9. Table Tennis Equipment
![Table Tennis Paddle](https://images.unsplash.com/photo-1581588667945-13abf4db4a58?w=400&h=300&fit=crop)
- **Table Tennis Paddle - Butterfly Timo Boll**
  - Description: Professional table tennis paddle with offensive rubber. Perfect balance of speed and spin.
  - Price: ₹45/hr
  - Stock: 8 available

### 10. Hockey Equipment
![Hockey Stick](https://images.unsplash.com/photo-1579504137364-ef0f3c6a7e2c?w=400&h=300&fit=crop)
- **Hockey Stick - Grays GX 3000**
  - Description: Field hockey stick with carbon composite construction. Excellent for both beginners and experienced players.
  - Price: ₹55/hr
  - Stock: 7 available

### Other Equipment
- **zaid**
  - Price: ₹9/hr
  - Stock: 80 available

- **Test Gear**
  - Description: Test gear for verification
  - Price: ₹5/hr
  - Stock: 10 available

## Setup Instructions

### Prerequisites
- Node.js (v14 or higher)
- Python (v3.8 or higher)
- MongoDB instance
- npm or yarn package manager

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```
   MONGO_URL="mongodb://localhost:27017"
   DB_NAME="test_database"
   JWT_SECRET=your_jwt_secret_key
   SUBSCRIPTION_PRICE=99.99
   ```

4. Run the backend server:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8002 --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables in `.env`:
   ```
   REACT_APP_BACKEND_URL=http://localhost:8002
   ```

4. Start the development server:
   ```bash
   npm start
   ```

## Usage Guide

### For Students
1. Register for an account using email/phone
2. Log in to your account
3. Upload your digital ID for verification
4. Wait for admin approval
5. Once approved, browse equipment and make rentals
6. Book turf slots as needed

### For Administrators
1. Log in with admin credentials
2. Navigate to the admin dashboard
3. Manage pending approvals for students
4. Add/update/delete equipment inventory
5. Approve/reject rental and booking requests
6. Monitor facility usage through reports

## Troubleshooting

### Common Issues
1. **CORS Errors**: Ensure backend server is running and CORS is properly configured
2. **Authentication Failures**: Check JWT secret key and token expiration settings
3. **Database Connection Issues**: Verify MongoDB connection string and database accessibility
4. **Port Conflicts**: Ensure ports 3000 (frontend) and 8002 (backend) are available

### Support
For technical issues, contact the development team or check the server logs for error details.

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License
This project is proprietary to the college sports facility and should not be distributed without permission.