import { useState, createContext } from "react";

export const NotifContext = createContext();
export const RegistrationContext = createContext();

export const InterfaceProvider = ({ children }) => {
  const [registrationData, setRegistrationData] = useState({ forRegistration: false });
  const [notifStack, setNotifStack] = useState([]);
  const addToNotifs = (notif) => {
    setNotifStack((prev) => {
      const newStack = [{...notif, id: crypto.randomUUID()}, ...prev];
      return newStack.splice(0, 5);
    });
  };

  return (
    <RegistrationContext.Provider value={{registrationData, setRegistrationData}}>
      <NotifContext.Provider value={{notifStack, addToNotifs, setNotifStack}}>
        {children}
      </NotifContext.Provider>
    </RegistrationContext.Provider>
  );
};