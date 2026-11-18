import React, { useState } from 'react';
import GearModal from './GearModal';

// SVG Icons
// const MinusIcon = () => (
//   <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
//     <line x1="5" y1="12" x2="19" y2="12"></line>
//   </svg>
// );
//
// const PlusIcon = () => (
//   <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
//     <line x1="12" y1="5" x2="12" y2="19"></line>
//     <line x1="5" y1="12" x2="19" y2="12"></line>
//   </svg>
// );

function RentGear({ gearItems, loading, error, onGearUpdate }) {
  const [selectedGear, setSelectedGear] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleRentClick = (gear) => {
    setSelectedGear(gear);
    setIsModalOpen(true);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-[#B3B3B3]">Loading gear items...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-red-500">Error: {error}</div>
      </div>
    );
  }

  // Filter out test products and unwanted items
  // But keep valid gear items that have images
  const filteredGearItems = gearItems.filter(gear => 
    !gear.name.toLowerCase().includes('test') && 
    !gear.name.toLowerCase().includes('zaid') &&
    !gear.name.toLowerCase().includes('sample') &&
    !gear.name.toLowerCase().includes('demo') &&
    gear.stock > 0  // Only show items that have stock
  );
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
          Rent Gear
        </h1>

        {filteredGearItems.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-[#B3B3B3]">
              {gearItems.length === 0 
                ? "No gear items available for rent at the moment." 
                : "No gear items available for rent at the moment. All items may be filtered out."
              }
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-7">
            {filteredGearItems.map((gear) => (
              <div
                key={gear.id}
                className="overflow-hidden"
                style={{
                  background: '#111111',
                  borderRadius: '18px',
                  padding: '22px',
                  boxShadow: '0 0 28px rgba(0,0,0,0.45)'
                }}
              >
                {/* Gear Image */}
                <div 
                  className="rounded-lg mb-4 overflow-hidden flex items-center justify-center"
                  style={{
                    height: '150px',
                    background: 'linear-gradient(45deg, #1A1A1A, #2A2A2A)'
                  }}
                >
                  {(() => {
                    let imagePath;
                    const name = gear.name.toLowerCase();
                    
                    // Use local images when available, otherwise use database URLs
                    if (name.includes('basketball')) {
                      imagePath = '/images/equipment/basketball.jpg';
                    } else if (name.includes('badminton')) {
                      imagePath = '/images/equipment/badminton.webp';
                    } else if (name.includes('cricket')) {
                      imagePath = '/images/equipment/cricket-bat.webp';
                    } else if (name.includes('football')) {
                      imagePath = '/images/equipment/football.jpg';
                    } else if (name.includes('tennis')) {
                      imagePath = '/images/equipment/racket.webp';
                    } else if (name.includes('volleyball')) {
                      imagePath = '/images/equipment/volleyball.webp';
                    } else if (name.includes('shoes') || name.includes('running')) {
                      imagePath = 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300&h=200&fit=crop';
                    } else if (name.includes('carrom')) {
                      imagePath = '/images/equipment/carrom.jpg';
                    } else {
                      // Use database image_url for other items
                      imagePath = gear.image_url || '/images/equipment/racket.webp';
                    }
                    
                    console.log(`Gear: ${gear.name}, Image path: ${imagePath}`);
                    return (
                      <img 
                        src={imagePath} 
                        alt={gear.name} 
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          console.log(`Image failed to load: ${imagePath}`);
                          e.target.style.display = 'none';
                        }}
                      />
                    );
                  })()}
                </div>

                <h3 
                  className="font-bold mb-1"
                  style={{
                    fontSize: '18px',
                    color: '#FFFFFF'
                  }}
                >
                  {gear.name}
                </h3>

                <div className="flex justify-between items-center mb-4">
                  <div 
                    className="font-bold"
                    style={{ color: '#D7FF2F' }}
                  >
                    ₹{gear.price_per_hour}/hr
                  </div>
                  <div 
                    className="text-sm"
                    style={{ color: '#B3B3B3' }}
                  >
                    Stock: {gear.stock}
                  </div>
                </div>

                <button
                  onClick={() => handleRentClick(gear)}
                  className="w-full font-bold transition-all hover:brightness-110"
                  style={{
                    background: '#D7FF2F',
                    color: '#000000',
                    borderRadius: '10px',
                    height: '46px'
                  }}
                >
                  Rent Now
                </button>
              </div>
            ))}
          </div>
        )}

        {isModalOpen && selectedGear && (
          <GearModal 
            gear={selectedGear} 
            onClose={() => setIsModalOpen(false)} 
            onGearUpdate={onGearUpdate}
          />
        )}
      </div>
    </div>
  );
}

export default RentGear;