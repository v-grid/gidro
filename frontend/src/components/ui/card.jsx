// src/components/ui/card.jsx

import React from 'react';

// Компонент Card
export function Card({ children, className = "" }) {
  return (
    <div className={`bg-white p-4 rounded-lg shadow-md ${className}`}>
      {children}
    </div>
  );
}

// Компонент CardContent
export function CardContent({ children }) {
  return <div className="text-gray-700">{children}</div>;
}
