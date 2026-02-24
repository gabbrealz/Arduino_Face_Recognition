import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, ScrollText, UserPlus, X } from 'lucide-react';

export default function AdminHomepage() {
  const [activePopup, setActivePopup] = useState(null);
  
  // New state variables for database connection
  const [students, setStudents] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const closePopup = () => setActivePopup(null);

  // Fetch data only when the "users" popup is opened
  useEffect(() => {
    if (activePopup === 'users') {
      fetchStudents();
    }
  }, [activePopup]);

  const fetchStudents = async () => {
    setIsLoading(true);
    try {
      // ⚠️ Replace '/api/students' with your actual backend URL/endpoint
      const response = await fetch('/api/students');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setStudents(data); // Save database rows to React state
    } catch (error) {
      console.error("Error fetching student list:", error);
    } finally {
      setIsLoading(false);
    }
  };

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
              onClick={(e) => e.stopPropagation()} 
            >
              <div className="popup_header">
                <h2>{activePopup === 'users' ? 'Student List' : 'System Logs'}</h2>
                <button onClick={closePopup} className="close_btn"><X size={20} /></button>
              </div>

              <div className="table_container">
                <table className="popup_table">
                  {activePopup === 'users' ? (
                    <>
                      <thead>
                        <tr>
                          <th>Student Number</th>
                          <th>Name</th>
                          {/* Removed Section to match your DB schema */}
                          <th>Student Email</th>
                        </tr>
                      </thead>
                      <tbody>
                        {isLoading ? (
                          <tr><td colSpan="3" style={{ textAlign: 'center' }}>Loading students...</td></tr>
                        ) : students.length > 0 ? (
                          // Dynamically map over the data fetched from PostgreSQL
                          students.map((student) => (
                            <tr key={student.id}>
                              <td>{student.student_number}</td>
                              <td>{student.full_name}</td>
                              <td>{student.student_email}</td>
                            </tr>
                          ))
                        ) : (
                          <tr><td colSpan="3" style={{ textAlign: 'center' }}>No students found.</td></tr>
                        )}
                      </tbody>
                    </>
                  ) : (
                    <>
                      <thead><tr><th>Name</th><th>StudentID</th><th>Attendance Time</th></tr></thead>
                      <tbody>
                        <tr><td>Alex Rivera</td><td>2024-00000</td><td>12:34 PM</td></tr>
                        <tr><td>Sarah Chen</td><td>2024-00000</td><td>12:34 PM</td></tr>
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