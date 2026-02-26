import { useState, useEffect, useContext } from "react";
import { NotifContext } from "../Contexts.jsx";
import "../Notifications.css"; // Import the CSS file below

export default function Notifications() {
  const { notifStack } = useContext(NotifContext);

  return (
    <div className="notif-wrapper">
      {notifStack.map((notif, index) => (
        <Notification key={notif.id} notif={notif} index={index} />
      ))}
    </div>
  );
}

function Notification({ notif, index }) {
  const { setNotifStack } = useContext(NotifContext);
  const [beginRemoval, setBeginRemoval] = useState(false);

  const closeNotif = () => {
    setBeginRemoval(true);
    setTimeout(() => {
      setNotifStack((prev) => prev.filter((entry) => entry.id !== notif.id));
    }, 250);
  };

  useEffect(() => {
    const timer = setTimeout(closeNotif, 5000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div
      className={`notif-card ${beginRemoval ? "exit" : ""}`}
      style={{
        transform: `translateX(-50%) translateY(${index * 6}px) scaleX(${1 - index * 0.05})`,
        zIndex: 200 - index,
        backgroundColor: notif.bgColor
      }}
    >
      <div className="notif-message">{notif.message}</div>
      
      <button
        className={`close-btn ${index === 0 ? "active" : ""}`}
        onClick={index !== 0 ? () => {} : closeNotif}
      >
        <svg
          viewBox="0 0 512.021 512.021"
          className="close-icon"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d="M301.258,256.01L502.645,54.645c12.501-12.501,12.501-32.769,0-45.269c-12.501-12.501-32.769-12.501-45.269,0l0,0   L256.01,210.762L54.645,9.376c-12.501-12.501-32.769-12.501-45.269,0s-12.501,32.769,0,45.269L210.762,256.01L9.376,457.376   c-12.501,12.501-12.501,32.769,0,45.269s32.769,12.501,45.269,0L256.01,301.258l201.365,201.387   c12.501,12.501,32.769,12.501,45.269,0c12.501-12.501,12.501-32.769,0-45.269L301.258,256.01z" />
        </svg>
      </button>
    </div>
  );
}