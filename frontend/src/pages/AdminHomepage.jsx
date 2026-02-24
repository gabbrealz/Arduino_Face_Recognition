import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, ScrollText, UserPlus, X } from 'lucide-react';

export default function AdminHomepage() {
  const [activePopup, setActivePopup] = useState(null);

  const closePopup = () => setActivePopup(null);

  return (
    <div className="admin_homepage">
      <motion.h1 initial={{ opacity: 0 }} animate={{ opacity: 1 }}>Management</motion.h1>

      <div className="admin_container">
        {/* Users Card - Opens Popup */}
        <motion.button className="users" onClick={() => setActivePopup('users')} whileHover={{ y: -5 }}>
          <Users size={24} />
          <span className="title">Students</span>
        </motion.button>

        {/* Logs Card - Opens Popup */}
        <motion.button className="logs" onClick={() => setActivePopup('logs')} whileHover={{ y: -5 }}>
          <ScrollText size={24} />
          <span className="title"> Attendance Logs</span>
        </motion.button>

        {/* Register Card - Static */}
        <button className="register">
          <UserPlus size={24} />
          <span className="title">Register Students</span>
        </button>
      </div>

      {/* Popup Overlay */}
      <AnimatePresence>
        {activePopup && (
          <div className="popup_overlay" onClick={closePopup}>
            <motion.div 
              className="popup_content"
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside
            >
              <div className="popup_header">
                <h2>{activePopup === 'users' ? 'User Directory' : 'System Logs'}</h2>
                <button onClick={closePopup} className="close_btn"><X size={20} /></button>
              </div>

              <div className="table_container">
                <table className="popup_table">
                  {activePopup === 'users' ? (
                    <>
                      <thead><tr><th>Name</th><th>StudentID</th><th>Attendance Time</th></tr></thead>
                      <tbody>
                        <tr><td>Alex Rivera</td><td>2024-00000</td><td>12:34 PM</td></tr>
                        <tr><td>Sarah Chen</td><td>2024-00000</td><td>12:34 PM</td></tr>
                      </tbody>
                    </>
                  ) : (
                    <>
                      <thead><tr><th>Action</th><th>Timestamp</th></tr></thead>
                      <tbody>
                        <tr><td>Login Success</td><td>10:45 AM</td></tr>
                        <tr><td>DB Backup</td><td>09:00 AM</td></tr>
                      </tbody>
                    </>
                  )}
                </table>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}