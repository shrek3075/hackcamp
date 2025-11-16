import { Link } from "react-router-dom";

const Calendar = () => {
  return (
    <div className="min-h-screen bg-[#d4b896]">
      {/* Navigation Bar */}
      <nav className="bg-[#5c4033] text-white px-8 py-4 flex items-center justify-between">
        <div className="flex gap-12">
          <Link to="/" className="hover:opacity-80 transition-opacity">Home</Link>
          <Link to="/details" className="hover:opacity-80 transition-opacity">Details</Link>
          <Link to="/plan" className="hover:opacity-80 transition-opacity">Plan</Link>
          <Link to="/history" className="hover:opacity-80 transition-opacity">History</Link>
        </div>
        <Link to="/auth" className="hover:opacity-80 transition-opacity">Log Out</Link>
      </nav>

      <div className="container mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold text-[#3d2817] mb-4">Calendar</h1>
        <p className="text-[#5c4033]">View your study schedule on the calendar.</p>
      </div>
    </div>
  );
};

export default Calendar;
