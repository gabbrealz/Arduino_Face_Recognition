import { useState, createContext } from "react";

export const NotifContext = createContext();

export const InterfaceProvider = ({ children }) => {
  const [notifStack, setNotifStack] = useState([]);
  const addToNotifs = (notif) => {
    setNotifStack((prev) => {
      const newStack = [{...notif, id: crypto.randomUUID()}, ...prev];
      return newStack.splice(0, 5);
    });
  };

  return (
    <NotifContext.Provider value={{notifStack, addToNotifs, setNotifStack}}>
      {children}
    </NotifContext.Provider>
  );
};