import React, { useState, useEffect, useCallback } from 'react';
import RentGear from './RentGear';
import TurfPicker from './TurfPicker';

// SVG Icons
const GridIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#D7FF2F" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="7" height="7"></rect>
    <rect x="14" y="3" width="7" height="7"></rect>
    <rect x="14" y="14" width="7" height="7"></rect>
    <rect x="3" y="14" width="7" height="7"></rect>
  </svg>
);

const ShoppingBagIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#D7FF2F" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
    <line x1="3" y1="6" x2="21" y2="6"></line>
    <path d="M16 10a4 4 0 0 1-8 0"></path>
  </svg>
);

const CalendarIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#D7FF2F" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
    <line x1="16" y1="2" x2="16" y2="6"></line>
    <line x1="8" y1="2" x2="8" y2="6"></line>
    <line x1="3" y1="10" x2="21" y2="10"></line>
  </svg>
);

const ClockIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#D7FF2F" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"></circle>
    <polyline points="12 6 12 12 16 14"></polyline>
  </svg>
);

const ChecklistIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#D7FF2F" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="9 11 12 14 22 4"></polyline>
    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
  </svg>
);

const BagIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#D7FF2F" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
    <line x1="3" y1="6" x2="21" y2="6"></line>
    <path d="M16 10a4 4 0 0 1-8 0"></path>
  </svg>
);

const LogoutIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
    <polyline points="16 17 21 12 16 7"></polyline>
    <line x1="21" y1="12" x2="9" y2="12"></line>
  </svg>
);

function StudentDashboard() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [gearItems, setGearItems] = useState([]);
  const [myRentals, setMyRentals] = useState([]);
  const [myBookings, setMyBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8002';

  const fetchData = useCallback(async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        window.location.href = '/';
        return;
      }

      // Fetch gear items
      const gearRes = await fetch(`${backendUrl}/api/gear/list`, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (!gearRes.ok) {
        throw new Error('Failed to load gear items');
      }

      const gearData = await gearRes.json();
      setGearItems(gearData.gear || []);

      // Fetch my rentals
      const rentalsRes = await fetch(`${backendUrl}/api/gear/my-rentals`, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (rentalsRes.ok) {
        const rentalsData = await rentalsRes.json();
        setMyRentals(rentalsData.rentals || []);
      }

      // Fetch my bookings
      const bookingsRes = await fetch(`${backendUrl}/api/bookings/user`, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (bookingsRes.ok) {
        const bookingsData = await bookingsRes.json();
        setMyBookings(bookingsData.bookings || []);
      }
    } catch (err) {
      setError(err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, [backendUrl]);

  useEffect(() => {
    fetchData();
  }, [backendUrl, fetchData]);

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    window.location.href = '/';
  };

  // Handler functions for rental buttons
  const handleExtendRental = async (rentalId) => {
    const token = localStorage.getItem('auth_token');
    if (!token) return;

    try {
      const res = await fetch(`${backendUrl}/api/rentals/${rentalId}/extend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      const result = await res.json();
      if (res.ok) {
        alert(result.message || 'Rental extended successfully!');
        // Refresh rentals data
        const rentalsRes = await fetch(`${backendUrl}/api/gear/my-rentals`, {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        });

        if (rentalsRes.ok) {
          const rentalsData = await rentalsRes.json();
          setMyRentals(rentalsData.rentals || []);
        }
        
        // Refresh gear items
        const gearRes = await fetch(`${backendUrl}/api/gear/list`, {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        });
        
        if (gearRes.ok) {
          const gearData = await gearRes.json();
          setGearItems(gearData.gear || []);
        }
      } else {
        alert(result.message || result.detail || 'Failed to extend rental');
      }
    } catch (err) {
      alert('Error extending rental');
    }
  };

  const handleReturnRental = async (rentalId) => {
    const token = localStorage.getItem('auth_token');
    if (!token) return;

    if (window.confirm('Are you sure you want to return this item?')) {
      try {
        const res = await fetch(`${backendUrl}/api/rentals/${rentalId}/return`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({}),
        });

        const result = await res.json();
        if (res.ok) {
          alert(result.message || 'Item returned successfully!');
          // Refresh rentals data
          const rentalsRes = await fetch(`${backendUrl}/api/gear/my-rentals`, {
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
          });

          if (rentalsRes.ok) {
            const rentalsData = await rentalsRes.json();
            setMyRentals(rentalsData.rentals || []);
          }
          
          // Refresh gear items
          const gearRes = await fetch(`${backendUrl}/api/gear/list`, {
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
          });
          
          if (gearRes.ok) {
            const gearData = await gearRes.json();
            setGearItems(gearData.gear || []);
          }
        } else {
          alert(result.message || result.detail || 'Failed to return item');
        }
      } catch (err) {
        alert('Error returning item');
      }
    }
  };

  // Handler functions for booking buttons
  const handleCancelBooking = async (bookingId) => {
    const token = localStorage.getItem('auth_token');
    if (!token) return;

    if (window.confirm('Are you sure you want to cancel this booking?')) {
      try {
        const res = await fetch(`${backendUrl}/api/bookings/${bookingId}/cancel`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({}),
        });

        const result = await res.json();
        if (res.ok) {
          alert(result.message || 'Booking cancelled successfully!');
          // Refresh bookings data
          const bookingsRes = await fetch(`${backendUrl}/api/bookings/user`, {
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
          });

          if (bookingsRes.ok) {
            const bookingsData = await bookingsRes.json();
            setMyBookings(bookingsData.bookings || []);
          }
          
          // Refresh gear items
          const gearRes = await fetch(`${backendUrl}/api/gear/list`, {
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
          });
          
          if (gearRes.ok) {
            const gearData = await gearRes.json();
            setGearItems(gearData.gear || []);
          }
        } else {
          alert(result.message || result.detail || 'Failed to cancel booking');
        }
      } catch (err) {
        alert('Error cancelling booking: ' + err.message);
      }
    }
  };

  // const handleViewBooking = (bookingId) => {
  //   // Navigate to booking details or show modal
  //   alert(`Viewing booking details for ID: ${bookingId}`);
  // };

  const renderMainContent = () => {
    // Filter out test products and unwanted items for display
    const filteredGearItems = gearItems.filter(gear => 
      !gear.name.toLowerCase().includes('test') && 
      !gear.name.toLowerCase().includes('zaid') &&
      !gear.name.toLowerCase().includes('sample') &&
      !gear.name.toLowerCase().includes('demo')
    );

    switch (activeTab) {
      case 'rent-gear':
        return <RentGear gearItems={gearItems} loading={loading} error={error} onGearUpdate={fetchData} />;
      case 'book-turf':
        return <TurfPicker />;
      case 'my-rentals':
        return (
          <div className="space-y-6">
            <div className="text-center py-8">
              <h2 className="text-2xl font-bold mb-4">Your Rentals</h2>
              <p className="text-[#B3B3B3]">View and manage your current gear rentals</p>
            </div>
            
            <div 
              className="p-5 rounded-[18px] border border-[#333333]"
              style={{
                background: 'rgba(17, 17, 17, 0.8)',
                boxShadow: '0 0 28px rgba(0,0,0,0.45)'
              }}
            >
              <div className="flex justify-between items-center mb-5">
                <h3 className="text-xl font-bold">Active Rentals</h3>
                <div className="px-3 py-1 rounded-full bg-[#D7FF2F] text-black text-sm font-bold">
                  {myRentals.length} Items
                </div>
              </div>
              
              <div className="space-y-4">
                {myRentals.map((rental) => (
                  <div key={rental.id} className="p-4 rounded-lg border border-[#333333]" style={{ background: '#0F0F0F' }}>
                    <div className="flex gap-4">
                      <div className="w-20 h-20 rounded-lg overflow-hidden flex-shrink-0" style={{ background: 'linear-gradient(45deg, #1A1A1A, #2A2A2A)' }}>
                        <img 
                          src={
                            rental.gear_name?.toLowerCase().includes('basketball') ? '/images/equipment/basketball.jpg' :
                            rental.gear_name?.toLowerCase().includes('tennis') ? 'https://images.unsplash.com/photo-1581588667945-13abf4db4a58?w=100&h=100&fit=crop' :
                            rental.gear_name?.toLowerCase().includes('badminton') ? 'https://images.unsplash.com/photo-1579504137364-ef0f3c6a7e2c?w=100&h=100&fit=crop' :
                            rental.gear_name?.toLowerCase().includes('football') ? 'https://images.unsplash.com/photo-1579504137364-ef0f3c6a7e2c?w=100&h=100&fit=crop' :
                            rental.gear_name?.toLowerCase().includes('cricket') ? 'https://images.unsplash.com/photo-1521205050117-aaae1fcac0d5?w=100&h=100&fit=crop' :
                            rental.gear_name?.toLowerCase().includes('volleyball') ? 'https://images.unsplash.com/photo-1581588667945-13abf4db4a58?w=100&h=100&fit=crop' :
                            rental.gear_name?.toLowerCase().includes('swimming') ? 'https://images.unsplash.com/photo-1530543787849-128d94430c6b?w=100&h=100&fit=crop' :
                            rental.gear_name?.toLowerCase().includes('gym') ? 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=100&h=100&fit=crop' :
                            'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=100&h=100&fit=crop'
                          } 
                          alt={rental.gear_name || 'Gear'} 
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-bold text-white">{rental.gear_name || 'Unknown Gear'}</h4>
                        <p className="text-[#B3B3B3] text-sm">Quantity: {rental.quantity}</p>
                        <div className="flex justify-between items-center mt-2">
                          <span className="text-[#D7FF2F] text-sm">Rented: {new Date(rental.created_at).toLocaleDateString()}</span>
                          <span className={`text-sm ${Math.max(0, Math.ceil((new Date(rental.due_time) - new Date()) / (1000 * 60 * 60))) <= 2 ? 'text-red-500' : 'text-[#B3B3B3]'}`}>
                            Due: {Math.max(0, Math.ceil((new Date(rental.due_time) - new Date()) / (1000 * 60 * 60)))} hrs
                          </span>
                        </div>
                        <div className="mt-2">
                          <span className="px-2 py-1 rounded text-xs font-medium" style={{ 
                            background: rental.status === 'pending' ? '#FFA500' : 
                                      rental.status === 'active' ? '#D7FF2F' : 
                                      rental.status === 'returned' ? '#666666' : 
                                      '#FF4444', 
                            color: rental.status === 'pending' ? '#000000' : 
                                   rental.status === 'active' ? '#000000' : 
                                   rental.status === 'returned' ? '#FFFFFF' : 
                                   '#FFFFFF'
                          }}>
                            {rental.status.charAt(0).toUpperCase() + rental.status.slice(1)}
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-2 flex-col justify-center">
                        {rental.status === 'active' && (
                          <button 
                            onClick={() => handleReturnRental(rental.id)}
                            className="px-3 py-1 rounded text-xs bg-[#D7FF2F] text-black font-medium hover:brightness-110 transition-all"
                          >
                            Return
                          </button>
                        )}
                        {rental.status === 'returned' && (
                          <span className="text-xs text-[#B3B3B3]">Returned</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      case 'my-bookings':
        return (
          <div className="space-y-6">
            <div className="text-center py-8">
              <h2 className="text-2xl font-bold mb-4">Your Bookings</h2>
              <p className="text-[#B3B3B3]">View and manage your turf bookings</p>
            </div>
            
            <div 
              className="p-5 rounded-[18px] border border-[#333333]"
              style={{
                background: 'rgba(17, 17, 17, 0.8)',
                boxShadow: '0 0 28px rgba(0,0,0,0.45)'
              }}
            >
              <h3 className="text-xl font-bold mb-5">Turf Bookings</h3>
              
              <div className="space-y-4">
                {myBookings.map((booking) => (
                  <div key={booking.id} className="p-4 rounded-lg border border-[#333333]" style={{ background: '#0F0F0F' }}>
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-bold text-white">{booking.type} Court</h4>
                        <p className="text-[#B3B3B3] text-sm">{new Date(booking.date).toLocaleDateString()}</p>
                        <p className="text-[#D7FF2F] text-sm">{booking.slot_time}</p>
                        <div className="mt-2">
                          <span className="px-2 py-1 rounded text-xs font-medium" style={{ 
                            background: booking.status === 'pending' ? '#FFA500' : 
                                      booking.status === 'approved' ? '#D7FF2F' : 
                                      booking.status === 'confirmed' ? '#D7FF2F' : 
                                      '#666666', 
                            color: booking.status === 'pending' ? '#000000' : '#000000' 
                          }}>
                            {booking.status === 'pending' ? 'Waiting for Approval' : 
                             booking.status === 'approved' ? 'Approved' : 
                             booking.status === 'confirmed' ? 'Confirmed' : 
                             booking.status}
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        {booking.status !== 'cancelled' && (
                          <button 
                            onClick={() => handleCancelBooking(booking.id)}
                            className="px-3 py-1 rounded text-xs bg-[#333333] text-white"
                          >
                            Cancel
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      default:
        return (
          <div className="space-y-6">
            {/* Enhanced Stats Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-5">
              {/* Available Gear Card - Enhanced */}
              <div 
                className="p-5 rounded-[18px] border border-[#333333] hover:border-[#D7FF2F] transition-all duration-300"
                style={{
                  background: 'rgba(17, 17, 17, 0.8)',
                  boxShadow: '0 0 28px rgba(0,0,0,0.45)'
                }}
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2.5 rounded-lg" style={{ background: 'rgba(215,255,47,0.1)' }}>
                    <BagIcon />
                  </div>
                  <div>
                    <h3 className="text-white font-bold text-lg">Available Gear</h3>
                    <p className="text-[#B3B3B3] text-sm">Browse and rent</p>
                  </div>
                </div>
                <p className="text-3xl font-bold" style={{ color: '#D7FF2F' }}>{filteredGearItems.length}</p>
                <div className="mt-3 pt-3 border-t border-[#333333]">
                  <p className="text-xs text-[#B3B3B3]">Last updated: Just now</p>
                </div>
              </div>

              {/* Turf & Courts Card - Enhanced */}
              <div 
                className="p-5 rounded-[18px] border border-[#333333] hover:border-[#D7FF2F] transition-all duration-300"
                style={{
                  background: 'rgba(17, 17, 17, 0.8)',
                  boxShadow: '0 0 28px rgba(0,0,0,0.45)'
                }}
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2.5 rounded-lg" style={{ background: 'rgba(215,255,47,0.1)' }}>
                    <CalendarIcon />
                  </div>
                  <div>
                    <h3 className="text-white font-bold text-lg">Turf & Courts</h3>
                    <p className="text-[#B3B3B3] text-sm">Book slots</p>
                  </div>
                </div>
                <p className="text-3xl font-bold" style={{ color: '#D7FF2F' }}>5</p>
                <div className="mt-3 pt-3 border-t border-[#333333]">
                  <p className="text-xs text-[#B3B3B3]">3 courts available</p>
                </div>
              </div>

              {/* Your Rentals Card - Enhanced */}
              <div 
                className="p-5 rounded-[18px] border border-[#333333] hover:border-[#D7FF2F] transition-all duration-300"
                style={{
                  background: 'rgba(17, 17, 17, 0.8)',
                  boxShadow: '0 0 28px rgba(0,0,0,0.45)'
                }}
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2.5 rounded-lg" style={{ background: 'rgba(215,255,47,0.1)' }}>
                    <ClockIcon />
                  </div>
                  <div>
                    <h3 className="text-white font-bold text-lg">Your Rentals</h3>
                    <p className="text-[#B3B3B3] text-sm">Currently active</p>
                  </div>
                </div>
                <p className="text-3xl font-bold" style={{ color: '#D7FF2F' }}>3</p>
                <div className="mt-3 pt-3 border-t border-[#333333]">
                  <p className="text-xs text-[#B3B3B3]">Next due: Dec 25, 2024</p>
                </div>
              </div>

              {/* Quick Actions Card */}
              <div 
                className="p-5 rounded-[18px] border border-[#333333] hover:border-[#D7FF2F] transition-all duration-300"
                style={{
                  background: 'rgba(17, 17, 17, 0.8)',
                  boxShadow: '0 0 28px rgba(0,0,0,0.45)'
                }}
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2.5 rounded-lg" style={{ background: 'rgba(215,255,47,0.1)' }}>
                    <ChecklistIcon />
                  </div>
                  <div>
                    <h3 className="text-white font-bold text-lg">Quick Actions</h3>
                    <p className="text-[#B3B3B3] text-sm">Popular tasks</p>
                  </div>
                </div>
                <div className="space-y-3 mt-4">
                  <button 
                    onClick={() => setActiveTab('rent-gear')}
                    className="w-full text-left text-sm py-2 px-3 rounded-lg bg-[#222222] hover:bg-[#2A2A2A] transition-colors"
                  >
                    Rent Gear
                  </button>
                  <button 
                    onClick={() => setActiveTab('book-turf')}
                    className="w-full text-left text-sm py-2 px-3 rounded-lg bg-[#222222] hover:bg-[#2A2A2A] transition-colors"
                  >
                    Book Turf
                  </button>
                </div>
              </div>
            </div>

            {/* Two-Column Layout for Additional Content */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              {/* Recent Activity Panel */}
              <div 
                className="lg:col-span-2 p-5 rounded-[18px] border border-[#333333]"
                style={{
                  background: 'rgba(17, 17, 17, 0.8)',
                  boxShadow: '0 0 28px rgba(0,0,0,0.45)'
                }}
              >
                <div className="flex items-center justify-between mb-5">
                  <h2 className="text-xl font-bold">Recent Activity</h2>
                  <button className="text-xs text-[#D7FF2F] hover:underline">View All</button>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-start gap-4 pb-4 border-b border-[#333333]">
                    <div className="mt-1 p-2 rounded-lg" style={{ background: 'rgba(215,255,47,0.1)' }}>
                      <ShoppingBagIcon />
                    </div>
                    <div>
                      <h3 className="font-medium">New Gear Added</h3>
                      <p className="text-sm text-[#B3B3B3]">Badminton Rackets (Yonex) added to inventory</p>
                      <p className="text-xs text-[#B3B3B3] mt-1">2 hours ago</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-4 pb-4 border-b border-[#333333]">
                    <div className="mt-1 p-2 rounded-lg" style={{ background: 'rgba(215,255,47,0.1)' }}>
                      <CalendarIcon />
                    </div>
                    <div>
                      <h3 className="font-medium">Court Maintenance</h3>
                      <p className="text-sm text-[#B3B3B3]">Tennis Court 2 will be closed for maintenance</p>
                      <p className="text-xs text-[#B3B3B3] mt-1">Yesterday</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-4">
                    <div className="mt-1 p-2 rounded-lg" style={{ background: 'rgba(215,255,47,0.1)' }}>
                      <ClockIcon />
                    </div>
                    <div>
                      <h3 className="font-medium">Booking Reminder</h3>
                      <p className="text-sm text-[#B3B3B3]">Your basketball court booking is tomorrow</p>
                      <p className="text-xs text-[#B3B3B3] mt-1">3 days ago</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Announcements & Tips Panel */}
              <div 
                className="p-5 rounded-[18px] border border-[#333333]"
                style={{
                  background: 'rgba(17, 17, 17, 0.8)',
                  boxShadow: '0 0 28px rgba(0,0,0,0.45)'
                }}
              >
                <h2 className="text-xl font-bold mb-5">Campus Updates</h2>
                
                <div className="space-y-4">
                  <div className="pb-4 border-b border-[#333333]">
                    <h3 className="font-bold text-[#D7FF2F] mb-2">New Equipment!</h3>
                    <p className="text-sm text-[#B3B3B3]">We've added 20 new tennis rackets to our inventory.</p>
                    <p className="text-xs text-[#B3B3B3] mt-2">Posted: Today</p>
                  </div>
                  
                  <div className="pb-4 border-b border-[#333333]">
                    <h3 className="font-bold text-[#D7FF2F] mb-2">Maintenance Notice</h3>
                    <p className="text-sm text-[#B3B3B3]">Football field will be closed this weekend for maintenance.</p>
                    <p className="text-xs text-[#B3B3B3] mt-2">Posted: Yesterday</p>
                  </div>
                  
                  <div>
                    <h3 className="font-bold text-[#D7FF2F] mb-2">Pro Tip</h3>
                    <p className="text-sm text-[#B3B3B3]">Book courts in advance to guarantee availability during peak hours.</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Usage Statistics */}
            <div 
              className="p-5 rounded-[18px] border border-[#333333]"
              style={{
                background: 'rgba(17, 17, 17, 0.8)',
                boxShadow: '0 0 28px rgba(0,0,0,0.45)'
              }}
            >
              <h2 className="text-xl font-bold mb-5">Your Usage Statistics</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                <div>
                  <h3 className="text-[#B3B3B3] text-sm mb-2">Gears Rented</h3>
                  <p className="text-2xl font-bold" style={{ color: '#D7FF2F' }}>12</p>
                  <div className="mt-2 h-2 bg-[#222222] rounded-full overflow-hidden">
                    <div className="h-full bg-[#D7FF2F]" style={{ width: '60%' }}></div>
                  </div>
                  <p className="text-xs text-[#B3B3B3] mt-2">+2 from last month</p>
                </div>
                
                <div>
                  <h3 className="text-[#B3B3B3] text-sm mb-2">Hours Booked</h3>
                  <p className="text-2xl font-bold" style={{ color: '#D7FF2F' }}>24</p>
                  <div className="mt-2 h-2 bg-[#222222] rounded-full overflow-hidden">
                    <div className="h-full bg-[#D7FF2F]" style={{ width: '40%' }}></div>
                  </div>
                  <p className="text-xs text-[#B3B3B3] mt-2">+5 from last month</p>
                </div>
                
                <div>
                  <h3 className="text-[#B3B3B3] text-sm mb-2">Favorite Sport</h3>
                  <p className="text-2xl font-bold" style={{ color: '#D7FF2F' }}>Badminton</p>
                  <div className="mt-2 h-2 bg-[#222222] rounded-full overflow-hidden">
                    <div className="h-full bg-[#D7FF2F]" style={{ width: '80%' }}></div>
                  </div>
                  <p className="text-xs text-[#B3B3B3] mt-2">40% of bookings</p>
                </div>
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg text-white relative overflow-hidden">
      <div className="fixed inset-0 bg-grid opacity-40 pointer-events-none" />
      <main className="relative z-10 max-w-6xl mx-auto px-6 xl:px-16 py-6">
        <header className="flex items-start justify-between mb-6">
          <div>
            <div className="text-[11px] font-semibold tracking-[0.32em] text-accent-green mb-3">
              STUDENT PORTAL
            </div>
            <h1 className="font-['Unbounded',system-ui,sans-serif] text-[56px] leading-[0.9] font-black mb-2">
              STUDENT DASHBOARD
            </h1>
            <p className="text-sm text-[#B3B3B3]">
              Access and manage your sports facility bookings.
            </p>
          </div>

          <button
            type="button"
            className="mt-2 inline-flex items-center gap-2 text-[11px] font-medium text-[#B3B3B3] hover:text-white transition-colors"
            onClick={handleLogout}
          >
            <span className="inline-flex h-7 w-7 items-center justify-center rounded-full border border-[#333333] bg-black/60">
              <LogoutIcon />
            </span>
            <span className="tracking-[0.18em] uppercase">Logout</span>
          </button>
        </header>

        <div className="flex pt-8">
          {/* Enhanced Sidebar with Reduced Visual Weight */}
          <aside 
            className="fixed top-0 left-0 bottom-0 w-[220px] overflow-y-auto pt-20"
            style={{
              background: 'rgba(13, 13, 13, 0.7)', // Reduced opacity for lighter appearance
              borderRight: '1px solid rgba(255,255,255,0.03)', // Lighter border
              backdropFilter: 'blur(6px)' // Reduced blur effect
            }}
          >
            <nav className="p-3 space-y-1"> {/* Reduced spacing between items */}
              {[
                { id: 'dashboard', label: 'Dashboard', icon: <GridIcon /> },
                { id: 'rent-gear', label: 'Rent Gear', icon: <ShoppingBagIcon /> },
                { id: 'book-turf', label: 'Book Turf', icon: <CalendarIcon /> },
                { id: 'my-rentals', label: 'My Rentals', icon: <ClockIcon /> },
                { id: 'my-bookings', label: 'My Bookings', icon: <ChecklistIcon /> }
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all duration-200 ${
                    activeTab === item.id 
                      ? 'bg-[#2A2A2A] text-white shadow-[0_0_15px_rgba(215,255,47,0.1)]' // Enhanced active state with subtle glow
                      : 'text-[#A0A0A0] hover:text-white hover:bg-[#1A1A1A]' // Muted inactive state
                  }`}
                >
                  <span className={`${activeTab === item.id ? 'text-[#D7FF2F]' : 'text-[#A0A0A0]'}`}>
                    {item.icon}
                  </span>
                  <span className="font-medium">{item.label}</span>
                </button>
              ))}
            </nav>
          </aside>

          {/* Main Content */}
          <main 
            className="flex-1 ml-[220px] p-6"
          >
            <div className="max-w-6xl mx-auto">
              {renderMainContent()}
            </div>
          </main>
        </div>
      </main>
    </div>
  );
}

export default StudentDashboard;