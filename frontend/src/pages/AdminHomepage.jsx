import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaUsers, FaClipboardList, FaUserPlus } from 'react-icons/fa';
import { MdClose } from 'react-icons/md';


function getDateString(timestampStr) {
  const date = new Date(timestampStr);
  return date.toISOString().split('T')[0];
}

function getTimeString(timestampStr) {
  const date = new Date(timestampStr);
  return date.toISOString().split('T')[1].split('.')[0];
}


export default function AdminHomepage() {
  const [activePopup, setActivePopup] = useState(null);
  const [logs, setLogs] = useState([]);
  const [students, setStudents] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchLogs = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/attendance');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setLogs(data);
    }
    catch (error) {
      console.error("Error fetching student list:", error);
    }
    finally {
      setIsLoading(false);
    }
  };

  const fetchStudents = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/students');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setStudents(data);
    }
    catch (error) {
      console.error("Error fetching student list:", error);
    }
    finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (activePopup === 'users') {
      fetchStudents();
    }
    else if (activePopup === 'logs') {
      fetchLogs();
    }
  }, [activePopup]);

  const closePopup = () => setActivePopup(null);

  return (
    <div className="admin_homepage">
      <motion.h1 initial={{ opacity: 0 }} animate={{ opacity: 1 }}>Admin Management</motion.h1>

      <div className="admin_container">
        <motion.button className="users" onClick={() => setActivePopup('users')} whileHover={{ y: -5 }}>
          <FaUsers size={24} />
          <span className="title">Students</span>
        </motion.button>

        <motion.button className="logs" onClick={() => setActivePopup('logs')} whileHover={{ y: -5 }}>
          <FaClipboardList size={24} />
          <span className="title"> Attendance Logs</span>
        </motion.button>

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
                          <th>Student Email</th>
                        </tr>
                      </thead>
                      <tbody>
                        {isLoading ? (
                          <tr><td colSpan="3" style={{ textAlign: 'center' }}>Loading students...</td></tr>
                        ) : students.length > 0 ? (
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
                          <th>Date</th>
                          <th>Time</th>
                          <th>Student Number</th>
                          <th>Student Email</th>
                          <th>Full Name</th>
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
                              <td>{getDateString(log.created_at)}</td>
                              <td>{getTimeString(log.created_at)}</td>
                              <td>{log.student_number}</td>
                              <td>{log.student_email}</td>
                              <td>{log.full_name}</td>
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