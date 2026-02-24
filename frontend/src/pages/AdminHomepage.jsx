import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// 1. Import from react-icons (using Font Awesome and Md sets)
import { FaUsers, FaClipboardList, FaUserPlus } from 'react-icons/fa';
import { MdClose } from 'react-icons/md';

export default function AdminHomepage() {
  const [activePopup, setActivePopup] = useState(null);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8080/attendance');
    socket.onmessage = (event) => {
      const newData = JSON.parse(event.data);
      setLogs((prevLogs) => [newData, ...prevLogs]);
    };
    socket.onerror = (error) => console.error("WebSocket Error:", error);
    return () => socket.close();
  }, []);
  
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
        {/* Updated Icon: FaUsers */}
        <motion.button className="users" onClick={() => setActivePopup('users')} whileHover={{ y: -5 }}>
          <FaUsers size={24} />
          <span className="title">Students</span>
        </motion.button>

        {/* Updated Icon: FaClipboardList */}
        <motion.button className="logs" onClick={() => setActivePopup('logs')} whileHover={{ y: -5 }}>
          <FaClipboardList size={24} />
          <span className="title"> Attendance Logs</span>
        </motion.button>

        {/* Updated Icon: FaUserPlus */}
        <button className="register">
          <FaUserPlus size={24} />
          <span className="title">Register Students</span>
        </button>
      </div>

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
                <h2>{activePopup === 'users' ? 'User Directory' : 'Attendance Logs'}</h2>
                {/* Updated Icon: MdClose */}
                <button onClick={closePopup} className="close_btn"><MdClose size={24} /></button>
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
                      <thead>
                        <tr>
                          <th>Name</th>
                          <th>Student Number</th>
                          <th>Attendance Time</th>
                          <th>Date</th>
                        </tr>
                      </thead>
                      <tbody>
                        {logs.length > 0 ? (
                          logs.map((log, index) => (
                            <motion.tr 
                              key={index}
                              initial={{ backgroundColor: "#e6f7ff" }}
                              animate={{ backgroundColor: "transparent" }}
                              transition={{ duration: 2 }}
                            >
                              <td>{log.name}</td>
                              <td>{log.studentNumber}</td>
                              <td>{log.time}</td>
                              <td>{log.date}</td>
                            </motion.tr>
                          ))
                        ) : (
                          <tr><td colSpan="4" style={{textAlign: 'center'}}>Waiting for logs...</td></tr>
                        )}
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