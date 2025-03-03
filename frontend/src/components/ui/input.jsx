// src/components/ui/input.jsx

import React from 'react';

export const Input = ({ value, onChange, placeholder, className, type = 'text' }) => {
  return (
    <input
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className={`px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`}
    />
  );
};
