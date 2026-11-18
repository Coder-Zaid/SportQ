import React, { useState, useEffect, useCallback } from 'react';

function TurfPicker() {
  const [selectedDate, setSelectedDate] = useState(0);
  const [selectedTurf, setSelectedTurf] = useState(null);
  const [selectedSlots, setSelectedSlots] = useState([]);
  const [userBookings, setUserBookings] = useState([]);
  const [turfAvailability, setTurfAvailability] = useState({});
  const [availableTurfs, /*setAvailableTurfs*/] = useState([
    { id: '1', name: 'Basketball Court A', type: 'basketball' },
    { id: '2', name: 'Basketball Court B', type: 'basketball' },
    { id: '3', name: 'Tennis Court A', type: 'tennis' },
    { id: '4', name: 'Tennis Court B', type: 'tennis' },
    { id: '5', name: 'Football Field', type: 'football' }
  ]);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8002';

  // Helper function to convert 24-hour format to 12-hour format
  const convertTo12HourFormat = (time24) => {
    const [hours, minutes] = time24.split(':');
    let h = parseInt(hours, 10);
    const ampm = h >= 12 ? 'PM' : 'AM';
    h = h % 12 || 12; // Convert 0 to 12
    return `${h}:${minutes} ${ampm}`;
  };

  const loadUserBookings = useCallback(async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) return;

      const res = await fetch(`${backendUrl}/api/bookings/user`, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (res.ok) {
        const data = await res.json();
        setUserBookings(data.bookings || []);
      }
    } catch (err) {
      console.error('Failed to load bookings:', err);
    }
  }, [backendUrl]);

  const loadTurfAvailability = useCallback(async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) return;
      
      // Load availability for all dates
      const newAvailability = {};
      for (let i = 0; i < 7; i++) {
        const date = new Date();
        date.setDate(date.getDate() + i);
        const dateKey = date.toISOString().split('T')[0];
        
        const res = await fetch(`${backendUrl}/api/turf/availability?date=${dateKey}`, {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        });
        
        if (res.ok) {
          const data = await res.json();
          // Transform the data to match our expected format
          const slotAvailability = {};
          data.slots.forEach(slot => {
            slotAvailability[slot.time] = slot.available ? 3 : 0; // Assuming 3 turfs per slot
          });
          newAvailability[dateKey] = slotAvailability;
        }
      }
      setTurfAvailability(newAvailability);
    } catch (err) {
      console.error('Failed to load availability:', err);
    }
  }, [backendUrl]);

  // Load user bookings and turf availability
  useEffect(() => {
    loadUserBookings();
    loadTurfAvailability();
  }, [loadUserBookings, loadTurfAvailability]);

  // Generate dates for the next 7 days
  const dates = [];
  for (let i = 0; i < 7; i++) {
    const date = new Date();
    date.setDate(date.getDate() + i);
    dates.push({
      day: date.toLocaleDateString('en-US', { weekday: 'short' }),
      date: date.getDate(),
      month: date.toLocaleDateString('en-US', { month: 'short' }),
      fullDate: date.toISOString().split('T')[0]
    });
  }

  // Sample time slots
  const timeSlots = [
    '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
    '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
    '18:00', '19:00', '20:00', '21:00'
  ];

  const toggleSlot = (slot) => {
    const dateKey = dates[selectedDate].fullDate;
    const availableCount = turfAvailability[dateKey]?.[slot] || 0;
    
    if (availableCount === 0) {
      return; // Don't allow selection of unavailable slots
    }
    
    // Check if user already has a booking for this date
    const hasBookingForDate = userBookings.some(booking => 
      booking.date === dateKey && booking.status !== 'cancelled'
    );
    
    if (hasBookingForDate) {
      alert('You can only book 1 turf per day. You already have a booking for this date.');
      return;
    }
    
    // Allow only one slot selection at a time
    if (selectedSlots.includes(slot)) {
      setSelectedSlots([]); // Deselect if already selected
    } else {
      setSelectedSlots([slot]); // Select only this slot
    }
  };

  const handleConfirmBooking = async () => {
    if (!selectedTurf) {
      alert('Please select a turf first');
      return;
    }
    
    if (selectedSlots.length === 0) {
      alert('Please select at least one time slot');
      return;
    }
    
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        alert('Please login to make a booking');
        return;
      }

      const dateKey = dates[selectedDate].fullDate;
      
      const res = await fetch(`${backendUrl}/api/bookings/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          date: dateKey,
          slots: selectedSlots,
          type: selectedTurf.type,
          status: 'pending'
        }),
      });

      console.log('Booking response status:', res.status);
      console.log('Booking response ok:', res.ok);
      console.log('Booking response headers:', res.headers);

      const result = await res.json();
      console.log('Booking response body:', result);

      if (res.ok) {
        alert(result.message || `Booking request submitted for ${selectedTurf.name} on slots: ${selectedSlots.join(', ')}. Waiting for admin approval.`);
        setSelectedSlots([]);
        setSelectedTurf(null);
        loadUserBookings(); // Reload bookings
        loadTurfAvailability(); // Reload availability
      } else {
        alert(result.message || result.detail || 'Failed to create booking');
      }
    } catch (err) {
      console.error('Booking error:', err);
      alert('Failed to create booking. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg text-white relative overflow-hidden">
      <div className="fixed inset-0 bg-grid opacity-40 pointer-events-none" />
      <div className="relative z-10 max-w-6xl mx-auto px-6 xl:px-16 py-6">
        <h1 
          className="font-bold mb-6"
          style={{
            fontSize: '28px',
            color: '#FFFFFF'
          }}
        >
          Book Turf / Court
        </h1>

        {/* Date Selector */}
        <div className="mb-8">
          <div className="flex gap-3 overflow-x-auto pb-2">
            {dates.map((date, index) => (
              <button
                key={index}
                onClick={() => setSelectedDate(index)}
                className="flex-shrink-0 flex flex-col items-center justify-center px-4 py-3 transition-all"
                style={{
                  background: selectedDate === index ? '#D7FF2F' : '#0D0D0D',
                  color: selectedDate === index ? '#000000' : '#FFFFFF',
                  borderRadius: '12px'
                }}
              >
                <div className="font-bold text-sm">{date.day}</div>
                <div className="font-bold text-lg">{date.date}</div>
                <div className="text-xs">{date.month}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Turf Selection */}
        {!selectedTurf && (
          <div className="mb-8">
            <h2 className="text-xl font-bold mb-4" style={{ color: '#FFFFFF' }}>
              Available Turfs & Courts
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {availableTurfs.map((turf) => (
                <button
                  key={turf.id}
                  onClick={() => setSelectedTurf(turf)}
                  className="p-4 rounded-lg text-left transition-all hover:brightness-110"
                  style={{
                    background: '#111111',
                    border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: '12px'
                  }}
                >
                  <h3 className="font-bold text-lg mb-1">{turf.name}</h3>
                  <p className="text-sm text-[#B3B3B3] capitalize">{turf.type} court</p>
                </button>
              ))}
            </div>
          </div>
        )}
        
        {/* Time Slots */}
        {selectedTurf && (
          <div className="mb-8">
            <div className="flex items-center mb-4">
              <button 
                onClick={() => setSelectedTurf(null)}
                className="mr-3 px-3 py-1 rounded text-sm bg-[#333333] hover:bg-[#444444]"
              >
                ← Back
              </button>
              <h2 className="text-xl font-bold" style={{ color: '#FFFFFF' }}>
                {selectedTurf.name} - Available Slots
              </h2>
            </div>
          
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {timeSlots.map((slot, index) => {
              const dateKey = dates[selectedDate].fullDate;
              const availableCount = turfAvailability[dateKey]?.[slot] || 0;
              const isSelected = selectedSlots.includes(slot);
              
              // Don't show slot if no turfs available
              if (availableCount === 0) {
                return null;
              }
              
              return (
                <button
                  key={index}
                  onClick={() => toggleSlot(slot)}
                  className="transition-all relative"
                  style={{
                    background: isSelected ? '#D7FF2F' : '#111111',
                    color: isSelected ? '#000000' : '#FFFFFF',
                    border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: '12px',
                    height: '48px'
                  }}
                >
                  <div>{convertTo12HourFormat(slot)}</div>
                  <div className="text-xs" style={{ 
                    opacity: 0.7,
                    fontSize: '10px'
                  }}>
                    {availableCount} left
                  </div>
                </button>
              );
            })}
          </div>

          {/* Selected Slots Summary */}
          {selectedSlots.length > 0 && (
            <div 
              className="mb-6 p-4 rounded-lg"
              style={{
                background: '#0F0F0F',
                border: '1px solid rgba(255,255,255,0.08)'
              }}
            >
              <h3 className="font-bold mb-2" style={{ color: '#FFFFFF' }}>
                Selected Slots ({selectedSlots.length})
              </h3>
              <div className="flex flex-wrap gap-2">
                {selectedSlots.map((slot, index) => (
                  <div 
                    key={index}
                    className="px-3 py-1 rounded-full text-sm"
                    style={{
                      background: '#D7FF2F',
                      color: '#000000'
                    }}
                  >
                    {convertTo12HourFormat(slot)}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Confirm Button */}
        <button
          onClick={handleConfirmBooking}
          className="w-full font-bold transition-all hover:brightness-110"
          style={{
            background: '#D7FF2F',
            color: '#000000',
            borderRadius: '10px',
            height: '52px',
            marginTop: '28px'
          }}
        >
          Confirm Booking
        </button>
      </div>
    </div>
  );
}

export default TurfPicker;