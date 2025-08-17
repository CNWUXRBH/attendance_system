import React from 'react';
import { RouterProvider } from 'react-router-dom';
import router from './router';
import { LoadingProvider } from './contexts/LoadingContext';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <LoadingProvider>
        <RouterProvider router={router} />
      </LoadingProvider>
    </ErrorBoundary>
  );
}

export default App;
