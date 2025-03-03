import { useState } from "react";
import Dashboard from "./components/Dashboard"; // Импортируем ваш Dashboard
import viteLogo from "/vite.svg";
import reactLogo from "./assets/react.svg";
import "./App.css";

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <div>
        
         <img src="/images/my-image.jpg" alt="Описание" style={{ width: "500px", height: "300px" }} />

        
        
      </div>
      <div className="flex items-center justify-center h-screen bg-blue-500 text-white">
      <h1 className="text-4xl font-bold">Добро пожаловать в систему мониторинга!</h1>
    </div>
      
      

      {/* Вставляем ваш Dashboard */}
      <Dashboard />
    </>
  );
}

export default App;
