import React from 'react'
import { Routes, Route } from 'react-router-dom'
import ChatPage from '../pages/widget/ChatPage'
import LeadGate from '../pages/widget/LeadGate'
import Dashboard from '../pages/admin/Dashboard'
import Users from '../pages/admin/Users'
import UserDetail from '../pages/admin/UserDetail'
import Documents from '../pages/admin/Documents'
import Statistics from '../pages/admin/Statistics'
import Settings from '../pages/admin/Settings'
import LiveChat from '../pages/admin/LiveChat'

export default function AppRouter() {
  return (
    <Routes>
      {/* Widget Routes */}
      <Route path="/" element={<LeadGate />} />
      <Route path="/chat" element={<ChatPage />} />
      
      {/* Admin Routes */}
      <Route path="/admin" element={<Dashboard />} />
      <Route path="/admin/live-chat" element={<LiveChat />} />
      <Route path="/admin/users" element={<Users />} />
      <Route path="/admin/users/:sessionId" element={<UserDetail />} />
      <Route path="/admin/documents" element={<Documents />} />
      <Route path="/admin/statistics" element={<Statistics />} />
      <Route path="/admin/settings" element={<Settings />} />
    </Routes>
  )
}
