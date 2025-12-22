import React, { useState, useEffect } from 'react';

import './App.css';
import { CalendarClock, Dumbbell, ShieldCheck, ScanLine, LogOut, Users, Activity, Ticket, Trash2 } from 'lucide-react';
import Register from './Register'; // Import the Register component
import StudentDashboardPage from './StudentDashboard'; // Import the new StudentDashboard component

function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('pending');
  const [reports, setReports] = useState(null);
  const [reportsError, setReportsError] = useState('');
  const [pendingStudents, setPendingStudents] = useState([]);
  const [pendingLoading, setPendingLoading] = useState(false);
  const [pendingError, setPendingError] = useState('');
  const [gearName, setGearName] = useState('');
  const [gearDescription, setGearDescription] = useState('');
  const [gearPrice, setGearPrice] = useState('');
  const [gearStock, setGearStock] = useState('');
  const [gearSubmitting, setGearSubmitting] = useState(false);
  const [gearError, setGearError] = useState('');
  const [gearInventory, setGearInventory] = useState([]);
  const [pendingBookings, setPendingBookings] = useState([]);
  const [pendingRentals, setPendingRentals] = useState([]);
  const [approvalsLoading, setApprovalsLoading] = useState(false);

  const backendUrl = 'http://localhost:8002';

  // Add logout function
  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    window.location.href = '/';
  };

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      window.location.href = '/';
      return;
    }

    const headers = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    };

    const fetchReports = async () => {
      try {
        const res = await fetch(`${backendUrl}/api/admin/reports`, { headers });
        if (res.status === 403) {
          localStorage.removeItem('auth_token');
          window.location.href = '/';
          return;
        }
        if (!res.ok) {
          throw new Error('Failed to load reports');
        }
        const data = await res.json();
        setReports(data);
      } catch (err) {
        setReportsError(err.message || 'Failed to load reports');
      }
    };

    const fetchPending = async () => {
      setPendingLoading(true);
      setPendingError('');
      try {
        const res = await fetch(`${backendUrl}/api/admin/pending-students`, { headers });
        if (res.status === 403) {
          localStorage.removeItem('auth_token');
          window.location.href = '/';
          return;
        }
        if (!res.ok) {
          throw new Error('Failed to load pending students');
        }
        const data = await res.json();
        setPendingStudents(data.pending_students || []);
      } catch (err) {
        setPendingError(err.message || 'Failed to load pending students');
      } finally {
        setPendingLoading(false);
      }
    };

    const fetchGear = async () => {
      try {
        const res = await fetch(`${backendUrl}/api/admin/gear`, { headers });
        if (res.status === 403) {
          localStorage.removeItem('auth_token');
          window.location.href = '/';
          return;
        }
        if (!res.ok) {
          throw new Error('Failed to load gear');
        }
        const data = await res.json();
        setGearInventory(data.gear || []);
      } catch (err) {
        // Keep UI quiet; optional logging hook
      }
    };

    const fetchPendingBookings = async () => {
      try {
        const res = await fetch(`${backendUrl}/api/admin/pending-bookings`, { headers });
        if (res.status === 403) {
          localStorage.removeItem('auth_token');
          window.location.href = '/';
          return;
        }
        if (!res.ok) {
          throw new Error('Failed to load pending bookings');
        }
        const data = await res.json();
        setPendingBookings(data.pending_bookings || []);
      } catch (err) {
        console.error('Failed to load pending bookings:', err);
      }
    };

    const fetchPendingRentals = async () => {
      try {
        const res = await fetch(`${backendUrl}/api/admin/pending-rentals`, { headers });
        if (res.status === 403) {
          localStorage.removeItem('auth_token');
          window.location.href = '/';
          return;
        }
        if (!res.ok) {
          throw new Error('Failed to load pending rentals');
        }
        const data = await res.json();
        setPendingRentals(data.pending_rentals || []);
      } catch (err) {
        console.error('Failed to load pending rentals:', err);
      }
    };

    fetchReports();
    fetchPending();
    fetchGear();
    fetchPendingBookings();
    fetchPendingRentals();
  }, []);

  const stats = [
    { id: 1, label: 'Total Users', value: reports?.total_users ?? '1', icon: Users },
    { id: 2, label: 'Pending Approvals', value: reports?.pending_approvals ?? '0', icon: ShieldCheck },
    { id: 3, label: 'Active Subscriptions', value: reports?.active_subscriptions ?? '0', icon: Activity },
    { id: 4, label: 'Total Bookings', value: reports?.total_bookings ?? '0', icon: Ticket },
  ];

  const handleApproval = async (userId, action) => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      return;
    }

    try {
      const res = await fetch(`${backendUrl}/api/admin/approve-student`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ user_id: userId, action }),
      });

      if (!res.ok) {
        throw new Error('Failed to update student status');
      }

      setPendingStudents((prev) => prev.filter((s) => s.id !== userId));
    } catch (err) {
      setPendingError(err.message || 'Failed to update student status');
    }
  };

  const handleAddGear = async (e) => {
    e.preventDefault();
    if (gearSubmitting) return;

    const token = localStorage.getItem('auth_token');
    if (!token) {
      return;
    }

    setGearSubmitting(true);
    setGearError('');

    try {
      const res = await fetch(`${backendUrl}/api/admin/gear`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: gearName,
          description: gearDescription,
          price_per_hour: parseFloat(gearPrice || '0'),
          stock: parseInt(gearStock || '0', 10),
          image_url: null,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || data.message || 'Failed to add gear');
      }

      // Refresh the gear inventory after adding new gear
      const refreshRes = await fetch(`${backendUrl}/api/admin/gear`, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (refreshRes.ok) {
        const refreshData = await refreshRes.json();
        setGearInventory(refreshData.gear || []);
      }

      // Clear form fields
      setGearName('');
      setGearDescription('');
      setGearPrice('');
      setGearStock('');
    } catch (err) {
      setGearError(err.message || 'Failed to add gear');
    } finally {
      setGearSubmitting(false);
    }
  };

  const handleDeleteGear = async (gearId) => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      return;
    }

    try {
      const res = await fetch(`${backendUrl}/api/admin/gear/${gearId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || data.message || 'Failed to delete gear');
      }

      // Remove the gear item from the local state
      setGearInventory((prev) => prev.filter((item) => item.id !== gearId));
    } catch (err) {
      // In a real app, you might want to show this error to the user
      console.error('Error deleting gear:', err.message);
    }
  };

  const handleBookingApproval = async (bookingId, action) => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      return;
    }

    try {
      const endpoint = action === 'approve' 
        ? `${backendUrl}/api/admin/approve-booking/${bookingId}`
        : `${backendUrl}/api/admin/reject-booking/${bookingId}`;
      
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to update booking status');
      }

      // Remove the booking from pending list
      setPendingBookings((prev) => prev.filter((b) => b.id !== bookingId));
      
      // Show success message
      alert(`Booking ${action}d successfully!`);
    } catch (err) {
      console.error(`Error ${action}ing booking:`, err.message);
      alert(`Error: ${err.message}`);
    }
  };

  const handleDeleteRental = async (rentalId) => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      return;
    }

    try {
      const res = await fetch(`${backendUrl}/api/admin/rentals/${rentalId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || data.message || 'Failed to delete rental');
      }

      // Remove the rental from the local state
      setPendingRentals((prev) => prev.filter((r) => r.id !== rentalId));
    } catch (err) {
      console.error('Error deleting rental:', err.message);
      alert(`Error: ${err.message}`);
    }
  };

  const handleRentalApproval = async (rentalId, action) => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      return;
    }

    try {
      const endpoint = action === 'approve' 
        ? `${backendUrl}/api/admin/approve-rental/${rentalId}`
        : `${backendUrl}/api/admin/reject-rental/${rentalId}`;
      
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to update rental status');
      }

      // Remove the rental from pending list
      setPendingRentals((prev) => prev.filter((r) => r.id !== rentalId));
      
      // Refresh gear inventory
      const gearRes = await fetch(`${backendUrl}/api/admin/gear`, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (gearRes.ok) {
        const gearData = await gearRes.json();
        setGearInventory(gearData.gear || []);
      }
      
      // Show success message
      alert(`Rental ${action}d successfully!`);
    } catch (err) {
      console.error(`Error ${action}ing rental:`, err.message);
      alert(`Error: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg text-white relative overflow-hidden">
      <div className="fixed inset-0 bg-grid opacity-40 pointer-events-none" />
      <main className="relative z-10 max-w-6xl mx-auto px-6 xl:px-16 py-10">
        <header className="flex items-start justify-between mb-9">
          <div>
            <div className="text-[11px] font-semibold tracking-[0.32em] text-accent-green mb-5">
              ADMIN PORTAL
            </div>
            <h1 className="font-['Unbounded',system-ui,sans-serif] text-[56px] leading-[0.9] font-black mb-3">
              ADMIN DASHBOARD
            </h1>
            <p className="text-sm text-[#B3B3B3] pt-1">
              Manage facility operations.
            </p>
          </div>

          <button
            type="button"
            className="mt-2 inline-flex items-center gap-2 text-[11px] font-medium text-[#B3B3B3] hover:text-white transition-colors"
            onClick={handleLogout}
          >
            <span className="inline-flex h-7 w-7 items-center justify-center rounded-full border border-[#333333] bg-black/60">
              <LogOut className="w-3.5 h-3.5" />
            </span>
            <span className="tracking-[0.18em] uppercase">Logout</span>
          </button>
        </header>

        <section className="mb-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-5">
            {stats.map(({ id, label, value, icon: Icon }) => (
              <div key={id} className="admin-stat-card">
                <div className="flex items-center justify-between mb-6">
                  <div className="admin-stat-icon">
                    <Icon className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-3xl font-semibold tracking-tight mb-1">{value}</div>
                <div className="text-[13px] text-[#B3B3B3]">{label}</div>
              </div>
            ))}
          </div>
          {reportsError && (
            <div className="mt-3 text-[11px] text-[#FF6B6B]">{reportsError}</div>
          )}
        </section>

        <section className="mt-4">
          <div className="admin-tab-group mb-6">
            <button
              type="button"
              className={`admin-tab ${activeTab === 'pending' ? 'admin-tab--active' : 'admin-tab--inactive'}`}
              onClick={() => setActiveTab('pending')}
            >
              Pending Students
            </button>
            <button
              type="button"
              className={`admin-tab ${activeTab === 'gear' ? 'admin-tab--active' : 'admin-tab--inactive'}`}
              onClick={() => setActiveTab('gear')}
            >
              Manage Gear
            </button>
            <button
              type="button"
              className={`admin-tab ${activeTab === 'approvals' ? 'admin-tab--active' : 'admin-tab--inactive'}`}
              onClick={() => setActiveTab('approvals')}
            >
              Approvals
            </button>
          </div>
          {activeTab === 'pending' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-7">
              <div className="admin-card lg:col-span-2">
                <h2 className="admin-card-title mb-2">PENDING STUDENTS</h2>
                <p className="text-[13px] text-[#B3B3B3] mb-6">Review and approve new student accounts.</p>
                {pendingLoading && (
                  <div className="admin-pending-empty">
                    <span className="text-[13px] text-[#B3B3B3]">Loading pending approvals...</span>
                  </div>
                )}

                {!pendingLoading && pendingStudents.length === 0 && !pendingError && (
                  <div className="admin-pending-empty">
                    <span className="text-[13px] text-[#B3B3B3]">No pending approvals</span>
                  </div>
                )}

                {!pendingLoading && pendingStudents.length > 0 && (
                  <div className="space-y-3">
                    {pendingStudents.map((student) => (
                      <div key={student.id} className="admin-pending-row">
                        <div>
                          <div className="text-sm font-semibold">{student.name}</div>
                          <div className="text-[12px] text-[#B3B3B3]">{student.email}</div>
                        </div>
                        <div className="flex gap-2">
                          <button
                            type="button"
                            className="admin-btn-approve"
                            onClick={() => handleApproval(student.id, 'approve')}
                          >
                            Approve
                          </button>
                          <button
                            type="button"
                            className="admin-btn-reject"
                            onClick={() => handleApproval(student.id, 'reject')}
                          >
                            Reject
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {pendingError && (
                  <div className="mt-4 text-[12px] text-[#FF6B6B]">{pendingError}</div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'gear' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-7">
              <div className="admin-card">
                <h2 className="admin-card-title mb-2">ADD NEW GEAR</h2>
                <p className="text-[13px] text-[#B3B3B3] mb-6">Add items to your inventory for students to rent.</p>

                <form className="space-y-4" onSubmit={handleAddGear}>
                  <div className="space-y-2">
                    <label className="admin-field-label">Name</label>
                    <input
                      className="admin-input"
                      placeholder="e.g. Basketball"
                      value={gearName}
                      onChange={(e) => setGearName(e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="admin-field-label">Description</label>
                    <textarea
                      className="admin-input admin-input--textarea"
                      rows="3"
                      placeholder="Short description of the gear"
                      value={gearDescription}
                      onChange={(e) => setGearDescription(e.target.value)}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="admin-field-label">Price per Hour (₹)</label>
                      <input
                        className="admin-input"
                        placeholder="5"
                        value={gearPrice}
                        onChange={(e) => setGearPrice(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="admin-field-label">Stock</label>
                      <input
                        className="admin-input"
                        placeholder="10"
                        value={gearStock}
                        onChange={(e) => setGearStock(e.target.value)}
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    className="mt-3 inline-flex h-11 px-6 items-center justify-center rounded-xl bg-[#C6FF07] text-black text-[13px] font-semibold tracking-[0.16em] uppercase shadow-[0_0_18px_rgba(198,255,7,0.55)] disabled:opacity-70 disabled:cursor-not-allowed"
                    disabled={gearSubmitting}
                  >
                    {gearSubmitting ? 'Adding...' : 'Add Gear'}
                  </button>
                </form>

                {gearError && (
                  <div className="mt-4 text-[12px] text-[#FF6B6B]">{gearError}</div>
                )}
              </div>

              <div className="admin-card">
                <h2 className="admin-card-title mb-2">GEAR INVENTORY</h2>
                <p className="text-[13px] text-[#B3B3B3] mb-5">Quick view of items available for booking.</p>

                <div className="space-y-3">
                  {gearInventory.map((item) => (
                    <div
                      key={item.id}
                      className="admin-gear-item"
                    >
                      <div>
                        <div className="text-sm font-semibold">{item.name}</div>
                        <div className="text-[12px] text-[#B3B3B3]">₹{item.price_per_hour}/hr</div>
                      </div>
                      <div className="text-[12px] text-[#B3B3B3]">
                        Stock: <span className="text-white font-medium">{item.stock}</span>
                      </div>
                      <button
                        type="button"
                        className="admin-btn-delete"
                        onClick={() => handleDeleteGear(item.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'approvals' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-7">
              <div className="admin-card">
                <h2 className="admin-card-title mb-2">PENDING BOOKINGS</h2>
                <p className="text-[13px] text-[#B3B3B3] mb-6">Review and approve turf booking requests.</p>
                
                <div className="space-y-3">
                  {pendingBookings.length === 0 ? (
                    <div className="admin-pending-empty">
                      <span className="text-[13px] text-[#B3B3B3]">No pending bookings</span>
                    </div>
                  ) : (
                    pendingBookings.map((booking) => (
                      <div key={booking.id} className="admin-pending-row">
                        <div>
                          <div className="text-sm font-semibold">{booking.type || 'Turf Court'}</div>
                          <div className="text-[12px] text-[#B3B3B3]">
                            {new Date(booking.date).toLocaleDateString()} - {booking.slot_time || 'Time slot'}
                          </div>
                          <div className="text-[12px] text-[#B3B3B3]">
                            Student: {booking.user?.name || booking.user?.email || 'Unknown'}
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button
                            type="button"
                            className="admin-btn-approve"
                            onClick={() => handleBookingApproval(booking.id, 'approve')}
                          >
                            Approve
                          </button>
                          <button
                            type="button"
                            className="admin-btn-reject"
                            onClick={() => handleBookingApproval(booking.id, 'reject')}
                          >
                            Reject
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              <div className="admin-card">
                <h2 className="admin-card-title mb-2">PENDING RENTALS</h2>
                <p className="text-[13px] text-[#B3B3B3] mb-6">Review and approve gear rental requests.</p>
                
                <div className="space-y-3">
                  {pendingRentals.length === 0 ? (
                    <div className="admin-pending-empty">
                      <span className="text-[13px] text-[#B3B3B3]">No pending rentals</span>
                    </div>
                  ) : (
                    pendingRentals.map((rental) => (
                      <div key={rental.id} className="admin-pending-row">
                        <div>
                          <div className="text-sm font-semibold">
                            {rental.gear?.name || 'Unknown Gear'} ({rental.quantity} units)
                          </div>
                          <div className="text-[12px] text-[#B3B3B3]">
                            Student: {rental.user?.name || rental.user?.email || 'Unknown'}
                          </div>
                          <div className="text-[12px] text-[#B3B3B3]">
                            Duration: 1 day
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button
                            type="button"
                            className="admin-btn-approve"
                            onClick={() => handleRentalApproval(rental.id, 'approve')}
                          >
                            Approve
                          </button>
                          <button
                            type="button"
                            className="admin-btn-reject"
                            onClick={() => handleRentalApproval(rental.id, 'reject')}
                          >
                            Reject
                          </button>
                          <button
                            type="button"
                            className="admin-btn-delete"
                            onClick={() => handleDeleteRental(rental.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

function LegacyStudentDashboard() {
  // Redirect to the new student dashboard
  React.useEffect(() => {
    window.location.href = '/student/dashboard';
  }, []);
  
  return (
    <div className="min-h-screen bg-dark-bg text-white relative overflow-hidden">
      <div className="fixed inset-0 bg-grid opacity-40 pointer-events-none" />
      <main className="relative z-10 max-w-5xl mx-auto px-6 xl:px-16 py-10">
        <h1 className="hero-title mb-6">Redirecting to Student Dashboard...</h1>
        <p className="text-gray-300 mb-8">
          If you are not redirected automatically, <a href="/student/dashboard" className="text-accent-green">click here</a>.
        </p>
      </main>
    </div>
  );
}

function App() {
  const [authMode, setAuthMode] = useState('email');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState('');

  const handleSignIn = async (e) => {
    e.preventDefault();
    setFeedback('');

    // Use environment variable or fallback to localhost:8002
    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8002';

    const payload = {
      password,
    };

    if (authMode === 'email') {
      payload.email = email;
    } else {
      payload.phone = phone;
    }

    setLoading(true);
    try {
      const res = await fetch(`${backendUrl}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        setFeedback(data.detail || 'Login failed');
        return;
      }

      // Store token for subsequent API calls
      if (data.token) {
        localStorage.setItem('auth_token', data.token);
      }

      const role = data.user?.role || 'user';
      setFeedback(`Signed in as ${role}`);

      // Simple role-based redirect
      if (role === 'admin') {
        window.location.href = '/admin';
      } else if (role === 'student') {
        window.location.href = '/student';
      }
    } catch (err) {
      setFeedback(err.message || 'Network error');
    } finally {
      setLoading(false);
    }
  };

  const path = window.location.pathname;

  if (path.startsWith('/admin')) {
    return <AdminDashboard />;
  }

  if (path.startsWith('/student/dashboard')) {
    return <StudentDashboardPage />;
  }

  if (path.startsWith('/student')) {
    return <LegacyStudentDashboard />;
  }

  // Handle registration route
  if (path.startsWith('/register')) {
    return <Register />;
  }

  return (
    <div className="min-h-screen bg-dark-bg text-white relative overflow-hidden">
      {/* Grid background */}
      <div className="fixed inset-0 bg-grid opacity-40 pointer-events-none" />

      {/* Main layout */}
      <main className="relative z-10 mx-auto px-6 xl:px-20 py-10 flex flex-col lg:flex-row gap-10 xl:gap-[84px] items-start lg:items-center justify-between max-w-6xl">

        {/* Left content */}
        <section className="w-full lg:w-[52%] max-w-xl">

          <h1 className="hero-title mb-4">
            <span className="hero-title-glow">SPORTS</span>
            <br />
            FACILITY
            <br />
            ACCESS
          </h1>

          <p className="text-gray-300 text-sm leading-relaxed mb-6 max-w-md">
            Book turfs, rent gear, and manage your sports facility access &mdash; all in one
            place.
          </p>

          {/* Feature cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-7 gap-y-7 max-w-xl mt-2">
            <div className="feature-card">
              <div className="feature-icon">
                <CalendarClock size={22} />
              </div>
              <div className="feature-text-main">Turf Booking</div>
              <div className="feature-text-sub">Reserve slots 24h in advance</div>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <Dumbbell size={22} />
              </div>
              <div className="feature-text-main">Gear Rental</div>
              <div className="feature-text-sub">Rent equipment easily</div>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <ShieldCheck size={22} />
              </div>
              <div className="feature-text-main">Secure Payments</div>
              <div className="feature-text-sub">Safe transactions</div>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <ScanLine size={22} />
              </div>
              <div className="feature-text-main">Digital ID</div>
              <div className="feature-text-sub">QR-based access</div>
            </div>
          </div>
        </section>

        {/* Right sign-in panel */}
        <aside className="signin-panel w-full lg:w-5/12 mt-8 lg:-mt-2">
          <h2 className="signin-title mb-6">SIGN IN</h2>

          {/* Email / Phone toggle */}
          <div className="signin-toggle mb-6">
            <button
              type="button"
              className={`signin-toggle-tab ${authMode === 'email' ? 'signin-toggle-tab--active' : 'signin-toggle-tab--inactive'}`}
              onClick={() => setAuthMode('email')}
            >
              Email
            </button>
            <button
              type="button"
              className={`signin-toggle-tab ${authMode === 'phone' ? 'signin-toggle-tab--active' : 'signin-toggle-tab--inactive'}`}
              onClick={() => setAuthMode('phone')}
            >
              Phone
            </button>
          </div>

          <form className="space-y-5" onSubmit={handleSignIn}>
            <div className="signin-field-group">
              <label className="signin-label">{authMode === 'email' ? 'College Email' : 'Phone Number'}</label>
              <input
                type={authMode === 'email' ? 'email' : 'tel'}
                className="signin-input"
                placeholder={authMode === 'email' ? 'student@college.edu' : '+91 98765 43210'}
                value={authMode === 'email' ? email : phone}
                onChange={(e) =>
                  authMode === 'email' ? setEmail(e.target.value) : setPhone(e.target.value)
                }
              />
            </div>

            <div className="signin-field-group">
              <label className="signin-label">Password</label>
              <input
                type="password"
                className="signin-input"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button type="submit" className="signin-button" disabled={loading}>
              {loading ? 'SIGNING IN...' : 'SIGN IN'}
            </button>
          </form>

          {feedback && (
            <div className="signin-footer-text mt-3 text-center text-xs">
              {feedback}
            </div>
          )}

          <div className="signin-footer-text mt-5 text-center text-xs">
            Don&apos;t have an account? <span className="signin-link" onClick={() => window.location.href = '/register'} style={{cursor: 'pointer'}}>Register here</span>
          </div>
        </aside>
      </main>
    </div>
  );
}

export default App;