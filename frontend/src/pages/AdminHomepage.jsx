import { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { FaUsers, FaClipboardList, FaUserPlus, FaEdit, FaTrash } from 'react-icons/fa';
import { MdClose } from 'react-icons/md';
import { NotifContext } from '../Contexts';
import Notifications from '../components/Notifications';

function getDateString(timestampStr) {
  const date = new Date(timestampStr);
  return date.toISOString().split('T')[0];
}

function getTimeString(timestampStr) {
  const date = new Date(timestampStr);
  return date.toISOString().split('T')[1].split('.')[0];
}

export default function AdminHomepage() {
  const { addToNotifs } = useContext(NotifContext);
  const navigate = useNavigate();

  const [activePopup, setActivePopup] = useState(null);
  const [logs, setLogs] = useState([]);
  const [students, setStudents] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const [editingStudentId, setEditingStudentId] = useState(null);
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
    setEditingStudentId(null);
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
        localStorage.setItem("STUDENT_NUMBER_FROM_REGISTRATION", data.student_number);
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

  const handleDeleteStudent = async (id) => {
    if (!window.confirm("Are you sure you want to delete this student?")) return;

    try {
      const response = await fetch(`http://localhost:8000/students?id=${id}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        fetchStudents();
        addToNotifs({
          bgColor: "#008000",
          message: "Student deleted successfully!"
        });
      } else {
        addToNotifs({
          bgColor: "#992020",
          message: "Failed to delete student"
        });
      }
    } catch (error) {
      console.error("Delete error:", error);
      addToNotifs({
        bgColor: "#992020",
        message: "An error occurred while deleting"
      });
    }
  };

  const handleEditClick = (student) => {
    setFormData({
      fullName: student.full_name,
      studentEmail: student.student_email
    });
    setEditingStudentId(student.id);
    setActivePopup('editStudent');
  };

  const handleUpdateSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch(`http://localhost:8000/students?id=${editingStudentId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.fullName,
          email: formData.studentEmail
        }),
      });

      if (response.ok) {
        setFormData({ fullName: '', studentEmail: '' });
        setEditingStudentId(null);
        setActivePopup('users');
        addToNotifs({
          bgColor: "#008000",
          message: "Student updated successfully!"
        });
      }
    } catch (error) {
      console.error("Update error:", error);
      addToNotifs({
        bgColor: "#992020",
        message: "An error occurred while updating"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteLog = async (logId) => {
    if (!window.confirm("Are you sure you want to delete this log entry?")) return;

    try {
      const response = await fetch(`http://localhost:8000/attendance?id=${logId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        fetchLogs();
        addToNotifs({
          bgColor: "#008000",
          message: "Log entry deleted successfully!"
        });
      }
    } catch (error) {
      console.error("Delete log error:", error);
      addToNotifs({
        bgColor: "#992020",
        message: "An error occurred while deleting log entry"
      });
    }
  };

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
                  {activePopup === 'editStudent' && 'Edit Student Info'}
                </h2>
              </div>

              <div className="table_container">
                {activePopup === 'register' || activePopup === 'editStudent' ? (
                  <form onSubmit={activePopup === 'register' ? handleRegisterSubmit : handleUpdateSubmit} className="registration_form">
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
                      {isLoading ? 'Processing...' : (activePopup === 'editStudent' ? 'Update Student' : 'Register Student')}
                    </button>
                    {activePopup === 'editStudent' && (
                      <button type="button" className="submit_btn" style={{marginTop: '10px', backGroundColor: '#ccc', color: '#333'}} onClick={() => { setActivePopup('users')}}>
                        Cancel
                      </button>
                    )}
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
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {isLoading ? (
                            <tr><td colSpan="4" style={{ textAlign: 'center' }}>Loading students...</td></tr>
                          ) : students.length > 0 ? (
                            students.map((student) => (
                              <tr key={student.id}>
                                <td>{student.student_number}</td>
                                <td>{student.full_name}</td>
                                <td>{student.student_email}</td>
                                <td style={{ gap: '15px'}}>
                                  <button onClick={() => handleEditClick(student)} style={{ background: 'none', border: 'none', color: '#5f8ab7', cursor: 'pointer' , marginRight: '10px'}}>
                                    <FaEdit size={18} />
                                  </button>
                                  <button onClick={() => handleDeleteStudent(student.id)} style={{ background: 'none', border: 'none', color: '#894b51', cursor: 'pointer' }}>
                                    <FaTrash size={18} />
                                  </button>
                                </td>
                              </tr>
                            ))
                          ) : (
                            <tr><td colSpan="4" style={{ textAlign: 'center' }}>No students found.</td></tr>
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
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {logs.length > 0 ? (
                            logs.map((log, index) => (
                              <motion.tr 
                                key={log.id || index}
                                initial={{ backgroundColor: "#e6f7ff" }}
                                animate={{ backgroundColor: "transparent" }}
                                transition={{ duration: 2 }}
                              >
                                <td>{getDateString(log.created_at)}</td>
                                <td>{getTimeString(log.created_at)}</td>
                                <td>{log.student_number}</td>
                                <td>{log.student_email}</td>
                                <td>{log.full_name}</td>
                                <td style={{ textAlign: 'center' }}>
                                  <button onClick={() => handleDeleteLog(log.id)} style={{ background: 'none', border: 'none', color: '#DC3545', cursor: 'pointer' }}>
                                    <FaTrash size={18} />
                                  </button>
                                </td>
                              </motion.tr>
                            ))
                          ) : (
                            <tr><td colSpan="6" style={{textAlign: 'center'}}>Waiting for logs...</td></tr>
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