import React, { useState } from 'react';

function Register() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState('');

  const handleRegister = async (e) => {
    e.preventDefault();
    setFeedback('');

    if (password !== confirmPassword) {
      setFeedback('Passwords do not match');
      return;
    }

    // Validate email domain - only allow @woxsen.edu.in
    if (!email.endsWith('@woxsen.edu.in')) {
      setFeedback('Only @woxsen.edu.in email addresses are allowed for registration');
      return;
    }

    setLoading(true);
    try {
      // Use environment variable or fallback to localhost:8002
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8002';
      
      const payload = {
        name: fullName,
        email,
        phone,
        password,
      };

      const res = await fetch(`${backendUrl}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        setFeedback(data.detail || 'Registration failed');
        return;
      }

      setFeedback('Registration successful! Please check your email for verification.');
      
      // Optionally redirect to login after a delay
      setTimeout(() => {
        window.location.href = '/';
      }, 2000);
    } catch (err) {
      setFeedback(err.message || 'Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Grid background */}
      <div 
        className="fixed inset-0 pointer-events-none"
        style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)`,
          backgroundSize: '20px 20px'
        }}
      />

      {/* Back button */}
      <button
        type="button"
        onClick={() => window.location.href = '/'}
        className="absolute top-6 left-1/2 transform -translate-x-1/2 text-[14px] text-[#B3B3B3] hover:opacity-80 transition-opacity"
      >
        ← Back to Login
      </button>

      {/* Registration card */}
      <div className="relative z-10 flex items-center justify-center min-h-screen px-4">
        <div 
          className="w-full max-w-[470px]"
          style={{
            background: '#111111',
            borderRadius: '20px',
            padding: '45px',
            boxShadow: '0px 0px 40px rgba(0,0,0,0.8)'
          }}
        >
          <h2 
            className="text-white mb-9"
            style={{
              fontWeight: 900,
              fontSize: '32px',
              lineHeight: 'normal'
            }}
          >
            REGISTER
          </h2>

          <form className="space-y-[22px]" onSubmit={handleRegister}>
            {/* Full Name Field */}
            <div className="space-y-2">
              <label 
                className="block text-[14px]"
                style={{ color: '#B3B3B3' }}
              >
                Full Name
              </label>
              <input
                type="text"
                placeholder="John Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full"
                style={{
                  background: '#0D0D0D',
                  height: '48px',
                  borderRadius: '6px',
                  color: '#FFFFFF',
                  border: '1px solid #222',
                  paddingLeft: '14px',
                  paddingRight: '14px'
                }}
                required
              />
            </div>

            {/* College Email Field */}
            <div className="space-y-2">
              <label 
                className="block text-[14px]"
                style={{ color: '#B3B3B3' }}
              >
                College Email
              </label>
              <input
                type="email"
                placeholder="student@woxsen.edu.in"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full"
                style={{
                  background: '#0D0D0D',
                  height: '48px',
                  borderRadius: '6px',
                  color: '#FFFFFF',
                  border: '1px solid #222',
                  paddingLeft: '14px',
                  paddingRight: '14px'
                }}
                required
              />
            </div>

            {/* Phone Number Field */}
            <div className="space-y-2">
              <label 
                className="block text-[14px]"
                style={{ color: '#B3B3B3' }}
              >
                Phone Number
              </label>
              <input
                type="tel"
                placeholder="1234567890"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full"
                style={{
                  background: '#0D0D0D',
                  height: '48px',
                  borderRadius: '6px',
                  color: '#FFFFFF',
                  border: '1px solid #222',
                  paddingLeft: '14px',
                  paddingRight: '14px'
                }}
                required
              />
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <label 
                className="block text-[14px]"
                style={{ color: '#B3B3B3' }}
              >
                Password
              </label>
              <input
                type="password"
                placeholder="●●●●●●●"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full"
                style={{
                  background: '#0D0D0D',
                  height: '48px',
                  borderRadius: '6px',
                  color: '#FFFFFF',
                  border: '1px solid #222',
                  paddingLeft: '14px',
                  paddingRight: '14px'
                }}
                required
              />
            </div>

            {/* Confirm Password Field */}
            <div className="space-y-2">
              <label 
                className="block text-[14px]"
                style={{ color: '#B3B3B3' }}
              >
                Confirm Password
              </label>
              <input
                type="password"
                placeholder="●●●●●●●"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full"
                style={{
                  background: '#0D0D0D',
                  height: '48px',
                  borderRadius: '6px',
                  color: '#FFFFFF',
                  border: '1px solid #222',
                  paddingLeft: '14px',
                  paddingRight: '14px'
                }}
                required
              />
            </div>

            {/* Register Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2"
              style={{
                background: '#D7FF2F',
                height: '52px',
                borderRadius: '6px',
                color: '#000000',
                fontWeight: 700,
                transition: 'filter 0.2s',
              }}
              onMouseOver={(e) => e.currentTarget.style.filter = 'brightness(1.05)'}
              onMouseOut={(e) => e.currentTarget.style.filter = 'none'}
            >
              {loading ? 'CREATING ACCOUNT...' : 'CREATE ACCOUNT'}
            </button>

            {feedback && (
              <div 
                className="text-center text-[13px]"
                style={{ 
                  color: feedback.includes('successful') ? '#D7FF2F' : '#FF6B6B',
                  marginTop: '10px'
                }}
              >
                {feedback}
              </div>
            )}
          </form>
        </div>
      </div>

    </div>
  );
}

export default Register;