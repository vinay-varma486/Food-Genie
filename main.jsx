import React from 'react';
import ReactDOM from 'react-dom/client';
import { FoodGenieApp } from './App';
import { LanguageProvider } from './LanguageContext';
import { AuthProvider } from './AuthContext';
import { ErrorBoundary } from './ErrorBoundary';
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <LanguageProvider>
        <AuthProvider>
          <FoodGenieApp />
        </AuthProvider>
      </LanguageProvider>
    </ErrorBoundary>
  </React.StrictMode>
);
