import { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { FaUsers, FaClipboardList, FaUserPlus } from 'react-icons/fa';
import { MdClose } from 'react-icons/md';
import { RegistrationContext } from '../Contexts';

function getDateString(timestampStr) {
  const date = new Date(timestampStr);
  return date.toISOString().split('T')[0];
}

function getTimeString(timestampStr) {
  const date = new Date(timestampStr);
  return date.toISOString().split('T')[1].split('.')[0];
}

export default function AdminHomepage() {
  const navigate = useNavigate();
  const { setRegistrationData } = useContext(RegistrationContext);
  const [activePopup, setActivePopup] = useState(null);
  const [logs, setLogs] = useState([]);
  const [students, setStudents] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // New State for Register Form
  const [formData, setFormData] = useState({ fullName: '', studentEmail: '' });

  const fetchLogs = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/attendance');
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setLogs(data);
    } catch (error) {
      console.error("Error fetching logs:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchStudents = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/students');
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
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
    if (activePopup === 'users') fetchStudents();
    else if (activePopup === 'logs') fetchLogs();
  }, [activePopup]);

  const closePopup = () => {
    setActivePopup(null);
    setFormData({ fullName: '', studentEmail: '' }); // Reset form on close
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/students', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.fullName,
          email: formData.studentEmail
        }),
      });
      const data = await response.json();

      if (response.ok) {
        closePopup();
        setRegistrationData({
          forRegistration: true,
          studentNumber: data.student_number
        });
        navigate("/");
      }

    }
    catch (error) {
      console.error("Registration error:", error);
    }
    finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="admin_homepage">
      <motion.h1 initial={{ opacity: 0 }} animate={{ opacity: 1 }}>Management</motion.h1>

      <div className="admin_container">
        <motion.button className="users" onClick={() => setActivePopup('users')} whileHover={{ y: -5 }}>
          <FaUsers size={24} />
          <span className="title">Students</span>
        </motion.button>

        <motion.button className="logs" onClick={() => setActivePopup('logs')} whileHover={{ y: -5 }}>
          <FaClipboardList size={24} />
          <span className="title">Attendance Logs</span>
        </motion.button>

        <motion.button className="register" onClick={() => setActivePopup('register')} whileHover={{ y: -5 }}>
          <FaUserPlus size={24} />
          <span className="title">Register Students</span>
        </motion.button>
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
                <h2>
                  {activePopup === 'users' && 'User Directory'}
                  {activePopup === 'logs' && 'Attendance Logs'}
                  {activePopup === 'register' && 'Student Registration'}
                </h2>
                <button onClick={closePopup} className="close_btn"><MdClose size={24} /></button>
              </div>

              <div className="table_container">
                {activePopup === 'register' ? (
                  <form onSubmit={handleRegisterSubmit} className="registration_form">
                    <div className="form_group">
                      <label className="form_label">Full Name</label>
                      <input 
                        type="text" 
                        required 
                        value={formData.fullName}
                        onChange={(e) => setFormData({...formData, fullName: e.target.value})}
                        placeholder="Student Name"
                      />
                    </div>
                    <div className="form_group">
                      <label className="form_label">Student Email</label>
                      <input 
                        type="email" 
                        required 
                        value={formData.studentEmail}
                        onChange={(e) => setFormData({...formData, studentEmail: e.target.value})}
                        placeholder="Student Email"
                      />
                    </div>
                    <button type="submit" className="submit_btn" disabled={isLoading}>
                      {isLoading ? 'Processing...' : 'Register Student'}
                    </button>
                  </form>
                ) : (
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
                            <tr><td colSpan="5" style={{textAlign: 'center'}}>Waiting for logs...</td></tr>
                          )}
                        </tbody>
                      </>
                    )}
                  </table>
                )}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}