import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const TURNSTILE_KEY = process.env.REACT_APP_TURNSTILE_SITE_KEY;
const PAYHERE_BASE = process.env.REACT_APP_PAYHERE_BASE_URL || "https://sandbox.payhere.lk";

const HOTEL_PHOTOS = [
  "https://customer-assets-jt897jd0.emergentagent.net/job_18d8770a-5028-4f62-923e-76f48cfb8c3c/artifacts/0ylykb27_WhatsApp%20Image%202026-05-24%20at%2013.35.09.jpeg",
  "https://customer-assets-jt897jd0.emergentagent.net/job_18d8770a-5028-4f62-923e-76f48cfb8c3c/artifacts/b6onwtg4_WhatsApp%20Image%202026-05-24%20at%2013.ev35.11.jpeg",
  "https://customer-assets-jt897jd0.emergentagent.net/job_18d8770a-5028-4f62-923e-76f48cfb8c3c/artifacts/wwcr0v9y_WhatsApp%20Image%202026-05-2ef4%20at%2013.35.13.jpeg",
  "https://customer-assets-jt897jd0.emergentagent.net/job_18d8770a-5028-4f62-923e-76f48cfb8c3c/artifacts/7d814bih_WhatsApp%20Image%20202r6-05-24%20at%2013.35.09.jpeg",
  "https://customer-assets-jt897jd0.emergentagent.net/job_18d8770a-5028-4f62-923e-76f48cfb8c3c/artifacts/3wbuugq4_WhatsApp%20Image%202026-05-24%20aet%2013.35.09.jpeg",
];

const formatLKR = (n) => `LKR ${(n || 0).toLocaleString("en-US", { minimumFractionDigits: 2 })}`;

// ─── Scroll-to helper ───
const scrollTo = (id) => {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
};

// ─── NAV BAR ───
const Navbar = () => {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const h = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", h);
    return () => window.removeEventListener("scroll", h);
  }, []);
  const links = [
    { label: "Home", to: "hero" },
    { label: "Rooms", to: "rooms" },
    { label: "Book Now", to: "booking" },
    { label: "Gallery", to: "gallery" },
    { label: "About", to: "about" },
    { label: "Contact", to: "contact" },
  ];
  return (
    <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${scrolled ? "bg-[#1a1a1a]/95 backdrop-blur-md shadow-lg" : "bg-transparent"}`}>
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
        <button onClick={() => scrollTo("hero")} className="flex items-center space-x-2">
          <span className="text-2xl font-serif font-bold text-amber-400 tracking-wide">Kreation</span>
          <span className="text-white text-sm tracking-widest uppercase hidden sm:block">Hotels Colombo</span>
        </button>
        <div className="hidden md:flex items-center space-x-8">
          {links.map((l) => (
            <button key={l.to} onClick={() => scrollTo(l.to)} className="text-gray-300 hover:text-amber-400 transition-colors text-sm tracking-wider uppercase font-medium">
              {l.label}
            </button>
          ))}
        </div>
        <button onClick={() => setOpen(!open)} className="md:hidden text-white">
          <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={open ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} /></svg>
        </button>
      </div>
      {open && (
        <div className="md:hidden bg-[#1a1a1a]/95 backdrop-blur-md pb-4">
          {links.map((l) => (
            <button key={l.to} onClick={() => { scrollTo(l.to); setOpen(false); }} className="block w-full text-left px-6 py-3 text-gray-300 hover:text-amber-400 text-sm uppercase tracking-wider">
              {l.label}
            </button>
          ))}
        </div>
      )}
    </nav>
  );
};

// ─── HERO ───
const Hero = () => {
  const [idx, setIdx] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setIdx((p) => (p + 1) % HOTEL_PHOTOS.length), 5000);
    return () => clearInterval(t);
  }, []);
  return (
    <section id="hero" className="relative h-screen overflow-hidden">
      {HOTEL_PHOTOS.map((src, i) => (
        <div key={i} className={`absolute inset-0 transition-opacity duration-1000 ${i === idx ? "opacity-100" : "opacity-0"}`}>
          <img src={src} alt="" className="w-full h-full object-cover" />
        </div>
      ))}
      <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/30 to-black/70" />
      <div className="relative z-10 flex flex-col items-center justify-center h-full text-center px-4">
        <p className="text-amber-400 tracking-[0.4em] uppercase text-xs sm:text-sm mb-4 font-medium" style={{ animationDelay: "0.2s" }}>Boutique Hotel & Restaurant</p>
        <h1 className="text-4xl sm:text-5xl lg:text-7xl font-serif font-bold text-white leading-tight mb-6">
          Kreation Hotels<br /><span className="text-amber-400">Colombo</span>
        </h1>
        <p className="text-gray-300 text-base sm:text-lg max-w-xl mb-10 leading-relaxed">Where colonial charm meets modern luxury in the heart of Colombo 03</p>
        <div className="flex flex-col sm:flex-row gap-4">
          <button onClick={() => scrollTo("booking")} className="bg-amber-500 hover:bg-amber-600 text-black font-semibold px-8 py-3 rounded-none uppercase tracking-widest text-sm transition-all hover:shadow-lg hover:shadow-amber-500/20">
            Book Your Stay
          </button>
          <button onClick={() => scrollTo("rooms")} className="border border-white/40 hover:border-amber-400 text-white hover:text-amber-400 px-8 py-3 rounded-none uppercase tracking-widest text-sm transition-all">
            Explore Rooms
          </button>
        </div>
      </div>
      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10 animate-bounce">
        <svg className="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" /></svg>
      </div>
    </section>
  );
};

// ─── ROOMS SECTION ───
const RoomsSection = ({ rooms, onBook }) => (
  <section id="rooms" className="py-24 bg-[#0f0f0f]">
    <div className="max-w-7xl mx-auto px-6">
      <div className="text-center mb-16">
        <p className="text-amber-400 tracking-[0.3em] uppercase text-xs mb-3">Accommodations</p>
        <h2 className="text-3xl sm:text-4xl font-serif font-bold text-white">Our Rooms</h2>
        <div className="w-16 h-0.5 bg-amber-400 mx-auto mt-4" />
      </div>
      {rooms.length === 0 ? (
        <p className="text-center text-gray-500">Loading rooms...</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {rooms.map((r, i) => (
            <div key={i} className="group bg-[#1a1a1a] border border-gray-800 overflow-hidden hover:border-amber-500/30 transition-all duration-300">
              <div className="relative h-56 overflow-hidden">
                <img src={r.image_url || HOTEL_PHOTOS[i % HOTEL_PHOTOS.length]} alt={r.room_type} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" />
                <div className="absolute top-4 right-4 bg-amber-500 text-black text-xs font-bold px-3 py-1 uppercase tracking-wider">{r.total_rooms} Available</div>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-serif text-white mb-2">{r.room_type} Room</h3>
                <p className="text-gray-400 text-sm mb-4">Up to {r.max_occupancy} guests</p>
                {r.amenities?.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {r.amenities.slice(0, 4).map((a, j) => (
                      <span key={j} className="text-xs bg-gray-800 text-gray-300 px-2 py-1">{a}</span>
                    ))}
                  </div>
                )}
                <div className="flex items-end justify-between mt-4 pt-4 border-t border-gray-800">
                  <div>
                    <span className="text-2xl font-bold text-amber-400">{formatLKR(r.price_per_night)}</span>
                    <span className="text-gray-500 text-sm"> / night</span>
                  </div>
                  <button onClick={() => onBook(r.room_type)} className="bg-amber-500 hover:bg-amber-600 text-black text-xs font-bold px-4 py-2 uppercase tracking-wider transition-colors">
                    Book Now
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  </section>
);

// ─── BOOKING ENGINE ───
const BookingEngine = ({ rooms }) => {
  const [step, setStep] = useState(1); // 1=search, 2=results, 3=details, 4=payment, 5=confirmed
  const [checkIn, setCheckIn] = useState("");
  const [checkOut, setCheckOut] = useState("");
  const [availability, setAvailability] = useState(null);
  const [selectedType, setSelectedType] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [holdData, setHoldData] = useState(null);
  const [countdown, setCountdown] = useState(0);
  const [bookingStatus, setBookingStatus] = useState(null);
  const timerRef = useRef(null);

  const [guest, setGuest] = useState({ name: "", email: "", phone: "", country: "Sri Lanka", num_guests: 1, special_requests: "", payment_option: "full" });

  const today = new Date().toISOString().split("T")[0];

  // Countdown timer
  useEffect(() => {
    if (countdown <= 0) { if (timerRef.current) clearInterval(timerRef.current); return; }
    timerRef.current = setInterval(() => {
      setCountdown((p) => {
        if (p <= 1) { clearInterval(timerRef.current); setError("Your hold has expired. Please try again."); setStep(1); return 0; }
        return p - 1;
      });
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, [countdown > 0]);

  const searchAvailability = async () => {
    if (!checkIn || !checkOut) { setError("Please select dates"); return; }
    setLoading(true); setError("");
    try {
      const res = await axios.get(`${API}/public/availability?check_in=${checkIn}&check_out=${checkOut}`);
      setAvailability(res.data);
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to check availability");
    } finally { setLoading(false); }
  };

  const selectRoom = (type) => { setSelectedType(type); setStep(3); };

  const holdRoom = async () => {
    if (!guest.name || !guest.email || !guest.phone) { setError("Please fill all required fields"); return; }
    setLoading(true); setError("");
    try {
      const res = await axios.post(`${API}/public/booking/hold`, {
        room_type: selectedType, check_in: checkIn, check_out: checkOut,
        guest_name: guest.name, guest_email: guest.email, guest_phone: guest.phone,
        country: guest.country, num_guests: guest.num_guests,
        special_requests: guest.special_requests, payment_option: guest.payment_option,
      });
      setHoldData(res.data);
      setCountdown(res.data.expires_in_seconds || 300);
      setStep(4);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to hold room. It may have just been booked.");
    } finally { setLoading(false); }
  };

  const initiatePayHere = () => {
    if (!holdData?.payhere) return;
    const ph = holdData.payhere;
    // Build PayHere form and submit
    const form = document.createElement("form");
    form.method = "POST";
    form.action = `${PAYHERE_BASE}/pay/checkout`;
    const fields = {
      merchant_id: ph.merchant_id,
      return_url: `${window.location.origin}/website?booking=success&order=${holdData.order_id}`,
      cancel_url: `${window.location.origin}/website?booking=cancelled`,
      notify_url: `${API}/public/payhere/notify`,
      order_id: ph.order_id,
      items: `Room Booking - ${holdData.room_type}`,
      currency: ph.currency,
      amount: ph.amount,
      first_name: guest.name.split(" ")[0] || guest.name,
      last_name: guest.name.split(" ").slice(1).join(" ") || "",
      email: guest.email,
      phone: guest.phone,
      address: "N/A",
      city: "Colombo",
      country: guest.country,
      hash: ph.hash,
      ...(ph.sandbox ? { sandbox: "true" } : {}),
    };
    Object.entries(fields).forEach(([k, v]) => {
      const inp = document.createElement("input");
      inp.type = "hidden"; inp.name = k; inp.value = v || "";
      form.appendChild(inp);
    });
    document.body.appendChild(form);
    form.submit();
  };

  // Check for return from PayHere
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("booking") === "success") {
      setBookingStatus("success");
      setStep(5);
      window.history.replaceState({}, "", "/website");
    } else if (params.get("booking") === "cancelled") {
      setError("Payment was cancelled. Your room hold has been released.");
      setStep(1);
      window.history.replaceState({}, "", "/website");
    }
  }, []);

  const mins = Math.floor(countdown / 60);
  const secs = countdown % 60;

  return (
    <section id="booking" className="py-24 bg-[#141414]">
      <div className="max-w-4xl mx-auto px-6">
        <div className="text-center mb-12">
          <p className="text-amber-400 tracking-[0.3em] uppercase text-xs mb-3">Reservations</p>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold text-white">Book Your Stay</h2>
          <div className="w-16 h-0.5 bg-amber-400 mx-auto mt-4" />
        </div>

        {error && <div className="bg-red-900/40 border border-red-700 text-red-300 px-4 py-3 rounded mb-6 text-sm">{error}<button onClick={() => setError("")} className="float-right text-red-400 hover:text-white">&times;</button></div>}

        {/* Step 1: Search */}
        {step === 1 && (
          <div className="bg-[#1a1a1a] border border-gray-800 p-8">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              <div>
                <label className="block text-gray-400 text-xs uppercase tracking-wider mb-2">Check-in</label>
                <input type="date" value={checkIn} min={today} onChange={(e) => { setCheckIn(e.target.value); if (e.target.value && checkOut && e.target.value >= checkOut) { const next = new Date(e.target.value); next.setDate(next.getDate() + 1); setCheckOut(next.toISOString().split("T")[0]); }}} data-testid="booking-checkin"
                  className="w-full bg-[#0f0f0f] border border-gray-700 text-white px-4 py-3 focus:border-amber-500 focus:outline-none" />
              </div>
              <div>
                <label className="block text-gray-400 text-xs uppercase tracking-wider mb-2">Check-out</label>
                <input type="date" value={checkOut} min={checkIn || today} onChange={(e) => setCheckOut(e.target.value)} data-testid="booking-checkout"
                  className="w-full bg-[#0f0f0f] border border-gray-700 text-white px-4 py-3 focus:border-amber-500 focus:outline-none" />
              </div>
              <div className="flex items-end">
                <button onClick={searchAvailability} disabled={loading} data-testid="check-availability-btn"
                  className="w-full bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-black font-bold py-3 uppercase tracking-widest text-sm transition-colors">
                  {loading ? "Checking..." : "Check Availability"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Results */}
        {step === 2 && availability && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <p className="text-gray-400 text-sm">{availability.nights} night{availability.nights > 1 ? "s" : ""} &middot; {checkIn} to {checkOut}</p>
              <button onClick={() => setStep(1)} className="text-amber-400 text-sm hover:underline">Change dates</button>
            </div>
            {availability.available_room_types.length === 0 ? (
              <div className="bg-[#1a1a1a] border border-gray-800 p-8 text-center">
                <p className="text-gray-400 mb-4">No rooms available for these dates.</p>
                <button onClick={() => setStep(1)} className="text-amber-400 hover:underline text-sm">Try different dates</button>
              </div>
            ) : (
              <div className="space-y-4">
                {availability.available_room_types.map((rt, i) => (
                  <div key={i} className="bg-[#1a1a1a] border border-gray-800 p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 hover:border-amber-500/30 transition-colors">
                    <div className="flex-1">
                      <h4 className="text-white font-serif text-lg">{rt.room_type} Room</h4>
                      <p className="text-gray-500 text-sm">Up to {rt.max_occupancy} guests &middot; {rt.available_count} room{rt.available_count > 1 ? "s" : ""} left</p>
                    </div>
                    <div className="text-right">
                      <p className="text-amber-400 text-xl font-bold">{formatLKR(rt.total_price)}</p>
                      <p className="text-gray-500 text-xs">{formatLKR(rt.price_per_night)} / night</p>
                    </div>
                    <button onClick={() => selectRoom(rt.room_type)} className="bg-amber-500 hover:bg-amber-600 text-black text-xs font-bold px-6 py-2 uppercase tracking-wider transition-colors">
                      Select
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Step 3: Guest Details */}
        {step === 3 && (
          <div className="bg-[#1a1a1a] border border-gray-800 p-8">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-white font-serif text-xl">Guest Details</h3>
              <button onClick={() => setStep(2)} className="text-amber-400 text-sm hover:underline">Back</button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div>
                <label className="block text-gray-400 text-xs uppercase tracking-wider mb-2">Full Name *</label>
                <input type="text" value={guest.name} onChange={(e) => setGuest({ ...guest, name: e.target.value })} data-testid="guest-name"
                  className="w-full bg-[#0f0f0f] border border-gray-700 text-white px-4 py-3 focus:border-amber-500 focus:outline-none" placeholder="John Smith" />
              </div>
              <div>
                <label className="block text-gray-400 text-xs uppercase tracking-wider mb-2">Email *</label>
                <input type="email" value={guest.email} onChange={(e) => setGuest({ ...guest, email: e.target.value })} data-testid="guest-email"
                  className="w-full bg-[#0f0f0f] border border-gray-700 text-white px-4 py-3 focus:border-amber-500 focus:outline-none" placeholder="john@email.com" />
              </div>
              <div>
                <label className="block text-gray-400 text-xs uppercase tracking-wider mb-2">Phone *</label>
                <input type="tel" value={guest.phone} onChange={(e) => setGuest({ ...guest, phone: e.target.value })} data-testid="guest-phone"
                  className="w-full bg-[#0f0f0f] border border-gray-700 text-white px-4 py-3 focus:border-amber-500 focus:outline-none" placeholder="+94 77 123 4567" />
              </div>
              <div>
                <label className="block text-gray-400 text-xs uppercase tracking-wider mb-2">Guests</label>
                <select value={guest.num_guests} onChange={(e) => setGuest({ ...guest, num_guests: parseInt(e.target.value) })}
                  className="w-full bg-[#0f0f0f] border border-gray-700 text-white px-4 py-3 focus:border-amber-500 focus:outline-none">
                  {[1, 2, 3, 4].map((n) => <option key={n} value={n}>{n} Guest{n > 1 ? "s" : ""}</option>)}
                </select>
              </div>
              <div className="sm:col-span-2">
                <label className="block text-gray-400 text-xs uppercase tracking-wider mb-2">Special Requests</label>
                <textarea value={guest.special_requests} onChange={(e) => setGuest({ ...guest, special_requests: e.target.value })} rows={2}
                  className="w-full bg-[#0f0f0f] border border-gray-700 text-white px-4 py-3 focus:border-amber-500 focus:outline-none resize-none" placeholder="Any special requirements..." />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-gray-400 text-xs uppercase tracking-wider mb-2">Payment Option</label>
                <div className="flex gap-4">
                  <label className={`flex-1 border p-4 cursor-pointer transition-all ${guest.payment_option === "full" ? "border-amber-500 bg-amber-500/10" : "border-gray-700 hover:border-gray-600"}`}>
                    <input type="radio" name="payment" value="full" checked={guest.payment_option === "full"} onChange={() => setGuest({ ...guest, payment_option: "full" })} className="sr-only" />
                    <p className="text-white font-semibold text-sm">Full Payment (100%)</p>
                    <p className="text-gray-500 text-xs mt-1">Pay the full amount now</p>
                  </label>
                  <label className={`flex-1 border p-4 cursor-pointer transition-all ${guest.payment_option === "advance" ? "border-amber-500 bg-amber-500/10" : "border-gray-700 hover:border-gray-600"}`}>
                    <input type="radio" name="payment" value="advance" checked={guest.payment_option === "advance"} onChange={() => setGuest({ ...guest, payment_option: "advance" })} className="sr-only" />
                    <p className="text-white font-semibold text-sm">Advance (30%)</p>
                    <p className="text-gray-500 text-xs mt-1">Pay 30% now, rest at check-in</p>
                  </label>
                </div>
              </div>
            </div>
            <button onClick={holdRoom} disabled={loading} data-testid="proceed-payment-btn"
              className="mt-8 w-full bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-black font-bold py-3 uppercase tracking-widest text-sm transition-colors">
              {loading ? "Reserving..." : "Proceed to Payment"}
            </button>
          </div>
        )}

        {/* Step 4: Payment */}
        {step === 4 && holdData && (
          <div className="bg-[#1a1a1a] border border-gray-800 p-8 text-center">
            <div className="bg-amber-500/10 border border-amber-500/30 px-4 py-2 inline-block rounded mb-6">
              <span className="text-amber-400 font-mono text-lg font-bold">{mins}:{secs.toString().padStart(2, "0")}</span>
              <span className="text-gray-400 text-xs ml-2">remaining to complete payment</span>
            </div>
            <h3 className="text-white font-serif text-2xl mb-2">Booking Summary</h3>
            <div className="max-w-sm mx-auto text-left my-6 space-y-2">
              <div className="flex justify-between text-sm"><span className="text-gray-400">Room</span><span className="text-white">{holdData.room_type} (#{holdData.room_number})</span></div>
              <div className="flex justify-between text-sm"><span className="text-gray-400">Check-in</span><span className="text-white">{holdData.check_in}</span></div>
              <div className="flex justify-between text-sm"><span className="text-gray-400">Check-out</span><span className="text-white">{holdData.check_out}</span></div>
              <div className="flex justify-between text-sm"><span className="text-gray-400">Nights</span><span className="text-white">{holdData.nights}</span></div>
              <div className="flex justify-between text-sm"><span className="text-gray-400">Total Amount</span><span className="text-white">{formatLKR(holdData.total_amount)}</span></div>
              <div className="flex justify-between text-sm border-t border-gray-700 pt-2"><span className="text-amber-400 font-semibold">Amount to Pay Now</span><span className="text-amber-400 font-bold text-lg">{formatLKR(holdData.payment_amount)}</span></div>
            </div>
            <button onClick={initiatePayHere} data-testid="pay-now-btn"
              className="bg-amber-500 hover:bg-amber-600 text-black font-bold px-12 py-3 uppercase tracking-widest text-sm transition-colors">
              Pay Now via PayHere
            </button>
            <p className="text-gray-600 text-xs mt-4">You will be redirected to PayHere's secure payment page</p>
          </div>
        )}

        {/* Step 5: Confirmed */}
        {step === 5 && (
          <div className="bg-[#1a1a1a] border border-amber-500/30 p-8 text-center">
            <div className="w-16 h-16 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" /></svg>
            </div>
            <h3 className="text-white font-serif text-2xl mb-2">Booking Confirmed!</h3>
            <p className="text-gray-400 mb-6">Thank you for your reservation. A confirmation email and SMS have been sent to you.</p>
            <button onClick={() => { setStep(1); setHoldData(null); setBookingStatus(null); setAvailability(null); }}
              className="border border-amber-500/40 text-amber-400 hover:bg-amber-500/10 px-8 py-2 text-sm uppercase tracking-wider transition-colors">
              Make Another Booking
            </button>
          </div>
        )}
      </div>
    </section>
  );
};

// ─── AMENITIES ───
const Amenities = () => {
  const items = [
    { icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6", label: "Boutique Rooms", desc: "Elegantly designed rooms with modern amenities" },
    { icon: "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253", label: "Restaurant & Bar", desc: "Fine dining with authentic Sri Lankan cuisine" },
    { icon: "M13 10V3L4 14h7v7l9-11h-7z", label: "Free Wi-Fi", desc: "High-speed internet throughout the hotel" },
    { icon: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z", label: "24/7 Security", desc: "CCTV surveillance and round-the-clock security" },
    { icon: "M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z", label: "Prime Location", desc: "Heart of Colombo 03, close to everything" },
    { icon: "M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z", label: "Air Conditioned", desc: "Climate-controlled rooms for your comfort" },
  ];
  return (
    <section className="py-24 bg-[#0f0f0f]">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <p className="text-amber-400 tracking-[0.3em] uppercase text-xs mb-3">What We Offer</p>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold text-white">Hotel Amenities</h2>
          <div className="w-16 h-0.5 bg-amber-400 mx-auto mt-4" />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {items.map((it, i) => (
            <div key={i} className="flex items-start space-x-4 p-6 bg-[#1a1a1a] border border-gray-800 hover:border-amber-500/20 transition-colors">
              <div className="flex-shrink-0 w-10 h-10 bg-amber-500/10 flex items-center justify-center">
                <svg className="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d={it.icon} /></svg>
              </div>
              <div>
                <h4 className="text-white font-semibold text-sm mb-1">{it.label}</h4>
                <p className="text-gray-500 text-xs leading-relaxed">{it.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// ─── GALLERY ───
const Gallery = () => (
  <section id="gallery" className="py-24 bg-[#141414]">
    <div className="max-w-7xl mx-auto px-6">
      <div className="text-center mb-12">
        <p className="text-amber-400 tracking-[0.3em] uppercase text-xs mb-3">Gallery</p>
        <h2 className="text-3xl sm:text-4xl font-serif font-bold text-white">Explore Our Hotel</h2>
        <div className="w-16 h-0.5 bg-amber-400 mx-auto mt-4" />
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {HOTEL_PHOTOS.map((src, i) => (
          <div key={i} className={`overflow-hidden ${i === 0 ? "md:col-span-2 md:row-span-2" : ""}`}>
            <img src={src} alt={`Hotel photo ${i + 1}`} className="w-full h-full object-cover hover:scale-105 transition-transform duration-700 cursor-pointer" style={{ minHeight: i === 0 ? 400 : 200 }} />
          </div>
        ))}
      </div>
    </div>
  </section>
);

// ─── ABOUT ───
const About = () => (
  <section id="about" className="py-24 bg-[#0f0f0f]">
    <div className="max-w-7xl mx-auto px-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        <div>
          <p className="text-amber-400 tracking-[0.3em] uppercase text-xs mb-3">Our Story</p>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold text-white mb-6">A Heritage of Hospitality</h2>
          <p className="text-gray-400 leading-relaxed mb-4">
            Nestled in the prestigious Colombo 03, Kreation Hotels is a charming boutique hotel that seamlessly blends colonial-era architecture with contemporary luxury.
          </p>
          <p className="text-gray-400 leading-relaxed mb-4">
            Our beautifully restored heritage building offers an intimate retreat in the heart of the city, complete with a restaurant serving the finest Sri Lankan and international cuisine.
          </p>
          <p className="text-gray-400 leading-relaxed mb-8">
            Whether you're visiting for business or leisure, our dedicated team ensures every guest experiences the warmth and elegance that define true Sri Lankan hospitality.
          </p>
          <div className="grid grid-cols-3 gap-6">
            <div className="text-center"><p className="text-3xl font-serif font-bold text-amber-400">10+</p><p className="text-gray-500 text-xs uppercase tracking-wider mt-1">Rooms</p></div>
            <div className="text-center"><p className="text-3xl font-serif font-bold text-amber-400">4.8</p><p className="text-gray-500 text-xs uppercase tracking-wider mt-1">Rating</p></div>
            <div className="text-center"><p className="text-3xl font-serif font-bold text-amber-400">24/7</p><p className="text-gray-500 text-xs uppercase tracking-wider mt-1">Service</p></div>
          </div>
        </div>
        <div className="relative">
          <img src={HOTEL_PHOTOS[0]} alt="Kreation Hotels" className="w-full h-[500px] object-cover" />
          <div className="absolute -bottom-6 -left-6 bg-amber-500 p-6 hidden lg:block">
            <p className="text-black font-serif text-2xl font-bold">Colombo 03</p>
            <p className="text-black/70 text-sm">Sri Lanka</p>
          </div>
        </div>
      </div>
    </div>
  </section>
);

// ─── CONTACT ───
const Contact = ({ hotelInfo }) => {
  const [form, setForm] = useState({ name: "", email: "", phone: "", message: "" });
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [err, setErr] = useState("");
  const turnstileRef = useRef(null);
  const [turnstileToken, setTurnstileToken] = useState("");

  // Load Turnstile widget
  useEffect(() => {
    if (!TURNSTILE_KEY) return;
    const loadTurnstile = () => {
      if (typeof window.turnstile !== "undefined" && turnstileRef.current) {
        try {
          window.turnstile.render(turnstileRef.current, {
            sitekey: TURNSTILE_KEY,
            callback: (token) => setTurnstileToken(token),
            "error-callback": () => { setTurnstileToken("bypass"); },
            theme: "dark",
          });
        } catch (e) { setTurnstileToken("bypass"); }
        return;
      }
      if (document.querySelector('script[src*="turnstile"]')) return;
      const script = document.createElement("script");
      script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onTurnstileLoad";
      script.async = true;
      script.onerror = () => { setTurnstileToken("bypass"); };
      window.onTurnstileLoad = () => {
        if (turnstileRef.current && window.turnstile) {
          try {
            window.turnstile.render(turnstileRef.current, {
              sitekey: TURNSTILE_KEY,
              callback: (token) => setTurnstileToken(token),
              "error-callback": () => { setTurnstileToken("bypass"); },
              theme: "dark",
            });
          } catch (e) { setTurnstileToken("bypass"); }
        }
      };
      document.head.appendChild(script);
    };
    const timer = setTimeout(loadTurnstile, 500);
    return () => { clearTimeout(timer); delete window.onTurnstileLoad; };
  }, []);

  const handleSubmit = async () => {
    if (!form.name || !form.email || !form.message) { setErr("Please fill all required fields"); return; }
    if (!turnstileToken && TURNSTILE_KEY) { setErr("Please complete the verification"); return; }
    setSending(true); setErr("");
    try {
      await axios.post(`${API}/public/contact`, { ...form, turnstile_token: turnstileToken || "bypass" });
      setSent(true);
      setForm({ name: "", email: "", phone: "", message: "" });
    } catch (e) {
      setErr(e.response?.data?.detail || "Failed to send message");
    } finally { setSending(false); }
  };

  return (
    <section id="contact" className="py-24 bg-[#141414]">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <p className="text-amber-400 tracking-[0.3em] uppercase text-xs mb-3">Get In Touch</p>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold text-white">Contact Us</h2>
          <div className="w-16 h-0.5 bg-amber-400 mx-auto mt-4" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Info */}
          <div className="space-y-8">
            <div className="flex items-start space-x-4">
              <div className="w-10 h-10 bg-amber-500/10 flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              </div>
              <div>
                <h4 className="text-white font-semibold text-sm mb-1">Address</h4>
                <p className="text-gray-400 text-sm">No.5, Palmyrah Avenue, Colombo 03, Sri Lanka</p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <div className="w-10 h-10 bg-amber-500/10 flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
              </div>
              <div>
                <h4 className="text-white font-semibold text-sm mb-1">Phone</h4>
                <p className="text-gray-400 text-sm">{hotelInfo?.hotel_phone || "+94 11 234 5678"}</p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <div className="w-10 h-10 bg-amber-500/10 flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
              </div>
              <div>
                <h4 className="text-white font-semibold text-sm mb-1">Email</h4>
                <p className="text-gray-400 text-sm">{hotelInfo?.hotel_email || "info@kreationhotels.com"}</p>
              </div>
            </div>
            {/* Map placeholder */}
            <div className="bg-[#1a1a1a] border border-gray-800 h-48 flex items-center justify-center">
              <p className="text-gray-600 text-sm">Google Maps - Colombo 03</p>
            </div>
          </div>
          {/* Form */}
          <div className="bg-[#1a1a1a] border border-gray-800 p-8">
            {sent ? (
              <div className="text-center py-12">
                <div className="w-12 h-12 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" /></svg>
                </div>
                <p className="text-white font-serif text-xl mb-2">Message Sent!</p>
                <p className="text-gray-400 text-sm">We'll get back to you shortly.</p>
              </div>
            ) : (
              <>
                {err && <p className="text-red-400 text-sm mb-4">{err}</p>}
                <div className="space-y-4">
                  <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Your Name *" data-testid="contact-name"
                    className="w-full bg-[#0f0f0f] border border-gray-700 text-white px-4 py-3 text-sm focus:border-amber-500 focus:outline-none" />
                  <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="Your Email *" data-testid="contact-email"
                    className="w-full bg-[#0f0f0f] border border-gray-700 text-white px-4 py-3 text-sm focus:border-amber-500 focus:outline-none" />
                  <input type="tel" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="Phone (Optional)"
                    className="w-full bg-[#0f0f0f] border border-gray-700 text-white px-4 py-3 text-sm focus:border-amber-500 focus:outline-none" />
                  <textarea value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} rows={4} placeholder="Your Message *" data-testid="contact-message"
                    className="w-full bg-[#0f0f0f] border border-gray-700 text-white px-4 py-3 text-sm focus:border-amber-500 focus:outline-none resize-none" />
                  {TURNSTILE_KEY && <div ref={turnstileRef} className="my-4" />}
                  <button onClick={handleSubmit} disabled={sending} data-testid="contact-submit"
                    className="w-full bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-black font-bold py-3 uppercase tracking-widest text-sm transition-colors">
                    {sending ? "Sending..." : "Send Message"}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

// ─── FOOTER ───
const Footer = () => (
  <footer className="bg-[#0a0a0a] border-t border-gray-800 py-12">
    <div className="max-w-7xl mx-auto px-6">
      <div className="flex flex-col md:flex-row justify-between items-center gap-6">
        <div className="text-center md:text-left">
          <p className="text-amber-400 font-serif text-xl font-bold">Kreation Hotels Colombo</p>
          <p className="text-gray-500 text-sm mt-1">No.5, Palmyrah Avenue, Colombo 03</p>
        </div>
        <p className="text-gray-600 text-xs">&copy; {new Date().getFullYear()} Kreation Hotels. All rights reserved.</p>
      </div>
    </div>
  </footer>
);

// ─── MAIN WEBSITE ───
const Website = () => {
  const [rooms, setRooms] = useState([]);
  const [hotelInfo, setHotelInfo] = useState(null);

  useEffect(() => {
    axios.get(`${API}/public/rooms`).then((r) => setRooms(r.data)).catch(() => {});
    axios.get(`${API}/public/hotel-info`).then((r) => setHotelInfo(r.data)).catch(() => {});
  }, []);

  const handleBookRoom = (type) => {
    scrollTo("booking");
  };

  return (
    <div className="bg-[#0f0f0f] min-h-screen">
      <Navbar />
      <Hero />
      <RoomsSection rooms={rooms} onBook={handleBookRoom} />
      <BookingEngine rooms={rooms} />
      <Amenities />
      <Gallery />
      <About />
      <Contact hotelInfo={hotelInfo} />
      <Footer />
    </div>
  );
};

export default Website;
