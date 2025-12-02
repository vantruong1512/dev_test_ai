import React from 'react'
import { Navigate } from 'react-router-dom'

// Future: JWT authentication
export default function ProtectedRoute({ children }) {
  const isAuthenticated = true // TODO: check JWT token
  
  if (!isAuthenticated) {
    return <Navigate to="/admin/login" replace />
  }
  
  return children
}
