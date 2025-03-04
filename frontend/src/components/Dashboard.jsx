import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import axios from "axios";

// Используем переменную окружения для API URL
const API_URL = import.meta.env.VITE_API_URL;

export default function Dashboard() {
  const [data, setData] = useState([]);
  const [settings, setSettings] = useState({ max_tds: "", min_tds: "", max_ph: "", min_ph: "" });
  const [auth, setAuth] = useState({ username: "", password: "" });
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    fetchData();
    fetchSettings();
  }, []);

  const fetchData = async () => {
    try {
      const response = await axios.get(`${API_URL}/data`);
      setData(response.data);
    } catch (error) {
      console.error("Ошибка загрузки данных", error);
    }
  };

  const fetchSettings = async () => {
    try {
      const response = await axios.get(`${API_URL}/settings`);
      setSettings(response.data);
    } catch (error) {
      console.error("Ошибка загрузки настроек", error);
    }
  };

  const loginForm = document.getElementById('loginForm');
loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    
    const formData = new FormData(loginForm);
    const username = formData.get('username');
    const password = formData.get('password');
    
    try {
        const response = await fetch(`/login?username=${username}&password=${password}`, {
            method: 'GET',
        });
        
        const result = await response.json();
        if (response.ok) {
            console.log('Login successful:', result);
        } else {
            console.log('Login failed:', result);
        }
    } catch (error) {
        console.error('Error during login request:', error);
    }
});


  const updateSettings = async () => {
    try {
      await axios.post(`${API_URL}/settings`, settings);
      alert("Настройки обновлены");
      fetchSettings();
    } catch (error) {
      console.error("Ошибка обновления настроек", error);
    }
  };

  return (
    <div className="p-4 grid gap-4">
      <Card>
        <CardContent>
          {data.map((item) => (
            <div key={item.id} className="border-b py-2">
              <p>TDS: {item.tds} | pH: {item.ph} | Уровень воды: {item.water_level}</p>
            </div>
          ))}
        </CardContent>
      </Card>
      
      {!isAuthenticated ? (
        <div>
          <h2 className="text-xl">Авторизация</h2>
          <Input placeholder="Логин" onChange={(e) => setAuth({ ...auth, username: e.target.value })} />
          <Input placeholder="Пароль" type="password" onChange={(e) => setAuth({ ...auth, password: e.target.value })} />
          <Button onClick={loginForm}>Войти</Button>
        </div>
      ) : (
        <Card>
          <CardContent>
            <h2 className="text-xl font-semibold">Настройки</h2>
            <Input placeholder="Макс. TDS" value={settings.max_tds} onChange={(e) => setSettings({ ...settings, max_tds: e.target.value })} />
            <Input placeholder="Мин. TDS" value={settings.min_tds} onChange={(e) => setSettings({ ...settings, min_tds: e.target.value })} />
            <Input placeholder="Макс. pH" value={settings.max_ph} onChange={(e) => setSettings({ ...settings, max_ph: e.target.value })} />
            <Input placeholder="Мин. pH" value={settings.min_ph} onChange={(e) => setSettings({ ...settings, min_ph: e.target.value })} />
            <Button onClick={updateSettings}>Сохранить</Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
