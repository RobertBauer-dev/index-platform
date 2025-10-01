import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Components
import Layout from './components/Layout.tsx';
import Dashboard from './pages/Dashboard.tsx';
import Indices from './pages/Indices.tsx';
import IndexDetail from './pages/IndexDetail.tsx';
import Securities from './pages/Securities.tsx';
import IndexBuilder from './pages/IndexBuilder.tsx';
import Login from './pages/Login.tsx';
import Register from './pages/Register.tsx';
import { AuthProvider } from './contexts/AuthContext.tsx';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="indices" element={<Indices />} />
              <Route path="indices/:id" element={<IndexDetail />} />
              <Route path="securities" element={<Securities />} />
              <Route path="builder" element={<IndexBuilder />} />
            </Route>
          </Routes>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
