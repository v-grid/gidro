// src/components/ui/button.jsx

import React from 'react';

export const Button = ({ onClick, children, className, type = 'button' }) => {
  return (
    <button
      type={type}
      onClick={onClick}
      className={`px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-700 ${className}`}
    >
      {children}
    </button>
  );
};
