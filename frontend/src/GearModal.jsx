import React, { useState } from 'react';

// SVG Icons
const XIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
);

const MinusIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="5" y1="12" x2="19" y2="12"></line>
  </svg>
);

const PlusIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="5" x2="12" y2="19"></line>
    <line x1="5" y1="12" x2="19" y2="12"></line>
  </svg>
);

function GearModal({ gear, onClose, onGearUpdate }) {
  const [quantity, setQuantity] = useState(1);

  const handleQuantityChange = (newQuantity) => {
    if (newQuantity >= 1 && newQuantity <= gear.stock) {
      setQuantity(newQuantity);
    }
  };

  const handleConfirmRent = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        alert('Please login to rent gear');
        return;
      }

      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8002';
      
      const res = await fetch(`${backendUrl}/api/rentals/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          gear_id: gear.id,
          quantity: quantity,
          status: 'pending'
        }),
      });

      const result = await res.json();
      if (res.ok) {
        alert(result.message || `Rental request submitted for ${quantity} ${gear.name}(s). Waiting for admin approval.`);
        // Call the callback to refresh gear items
        if (onGearUpdate) {
          onGearUpdate();
        }
        onClose();
      } else {
        // Only show error if the response actually indicates an error
        const errorMessage = result.detail || result.message || 'Failed to create rental request';
        if (res.status >= 400) {
          alert(errorMessage);
        }
      }
    } catch (err) {
      console.error('Rental error:', err);
      alert('Failed to create rental request. Please try again.');
    }
  };

  // Handle backdrop click to close modal
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.7)' }}
      onClick={handleBackdropClick}
    >
      <div 
        className="relative w-full max-w-[480px] overflow-hidden"
        style={{
          background: '#111111',
          borderRadius: '18px',
          boxShadow: '0 0 50px rgba(0,0,0,0.80)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onClose();
          }}
          className="absolute top-4 right-4 p-2 rounded-full hover:bg-[#2A2A2A] transition-colors"
        >
          <XIcon />
        </button>

        {/* Gear Image Placeholder */}
        <div 
          className="w-full flex items-center justify-center overflow-hidden"
          style={{
            height: '200px',
            background: 'linear-gradient(45deg, #1A1A1A, #2A2A2A)'
          }}
        >
          <img 
            src={gear.image_url || (
              gear.name.toLowerCase().includes('basketball') ? '/images/equipment/basketball.jpg' :
              gear.name.toLowerCase().includes('tennis') ? 'https://images.unsplash.com/photo-1581588667945-13abf4db4a58?w=400&h=300&fit=crop' :
              gear.name.toLowerCase().includes('badminton') ? '/images/equipment/badminton.webp' :
              gear.name.toLowerCase().includes('cricket') ? '/images/equipment/cricket-bat.webp' :
              gear.name.toLowerCase().includes('football') ? '/images/equipment/football.jpg' :
              gear.name.toLowerCase().includes('volleyball') ? '/images/equipment/volleyball.webp' :
              gear.name.toLowerCase().includes('swimming') ? 'https://images.unsplash.com/photo-1530543787849-128d94430c6b?w=400&h=300&fit=crop' :
              gear.name.toLowerCase().includes('gym') ? 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=400&h=300&fit=crop' :
              gear.name.toLowerCase().includes('table tennis') ? 'https://images.unsplash.com/photo-1552667466-07770ae110d?w=400&h=300&fit=crop' :
              gear.name.toLowerCase().includes('squash') ? 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=300&fit=crop' :
              gear.name.toLowerCase().includes('chess') ? 'https://images.unsplash.com/photo-1522748335274-9a3f7e2e6e76?w=400&h=300&fit=crop' :
              gear.name.toLowerCase().includes('carrom') ? 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=300&fit=crop' :
              '/images/equipment/racket.webp'
            )} 
            alt={gear.name} 
            className="w-full h-full object-cover"
          />
        </div>

        <div className="p-6">
          <h2 
            className="font-extrabold mb-2"
            style={{
              color: '#FFFFFF',
              fontSize: '20px'
            }}
          >
            {gear.name}
          </h2>

          <p 
            className="mb-4"
            style={{ color: '#B3B3B3' }}
          >
            {gear.description}
          </p>

          <div className="flex justify-between items-center mb-6">
            <div>
              <div 
                className="font-bold text-xl"
                style={{ color: '#D7FF2F' }}
              >
                ₹{gear.price_per_hour}/hr
              </div>
              <div 
                className="text-sm mt-1"
                style={{ color: '#B3B3B3' }}
              >
                Stock: {gear.stock} available
              </div>
            </div>

            {/* Quantity Selector */}
            <div 
              className="flex items-center"
              style={{
                background: '#0F0F0F',
                border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: '10px'
              }}
            >
              <button
                onClick={() => handleQuantityChange(quantity - 1)}
                disabled={quantity <= 1}
                className="p-3 disabled:opacity-30 hover:bg-[#2A2A2A] rounded-l-lg transition-colors"
              >
                <MinusIcon />
              </button>
              <div 
                className="px-6 font-bold text-lg"
                style={{ color: '#FFFFFF', minWidth: '50px', textAlign: 'center' }}
              >
                {quantity}
              </div>
              <button
                onClick={() => handleQuantityChange(quantity + 1)}
                disabled={quantity >= gear.stock}
                className="p-3 disabled:opacity-30 hover:bg-[#2A2A2A] rounded-r-lg transition-colors"
              >
                <PlusIcon />
              </button>
            </div>
          </div>

          {/* Confirm Button */}
          <button
            onClick={handleConfirmRent}
            className="w-full font-bold transition-all hover:brightness-110"
            style={{
              background: '#D7FF2F',
              color: '#000000',
              borderRadius: '10px',
              height: '48px'
            }}
          >
            Confirm Rent
          </button>
        </div>
      </div>
    </div>
  );
}

export default GearModal;