import React from 'react';
import { Link } from 'react-router-dom';
import { Users, FileText, BarChart3, Settings, MessageSquare } from 'lucide-react';

export default function Dashboard() {
  const menuItems = [
    {
      title: 'Live Chat',
      description: 'Chat trực tiếp với người dùng',
      icon: MessageSquare,
      path: '/admin/live-chat',
      color: 'from-green-500 to-emerald-600'
    },
    {
      title: 'Users',
      description: 'Quản lý người dùng và phiên chat',
      icon: Users,
      path: '/admin/users',
      color: 'from-blue-500 to-blue-600'
    },
    {
      title: 'Documents',
      description: 'Quản lý tài liệu kiến thức',
      icon: FileText,
      path: '/admin/documents',
      color: 'from-purple-500 to-purple-600'
    },
    {
      title: 'Statistics',
      description: 'Thống kê và phân tích',
      icon: BarChart3,
      path: '/admin/statistics',
      color: 'from-yellow-500 to-orange-600'
    },
    {
      title: 'Settings',
      description: 'Cài đặt hệ thống',
      icon: Settings,
      path: '/admin/settings',
      color: 'from-gray-500 to-gray-600'
    },
  ];

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Admin Dashboard</h1>
          <p className="text-gray-600">Quản lý chatbot AI RAG</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden group"
            >
              <div className={`h-2 bg-gradient-to-r ${item.color}`} />
              <div className="p-6">
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${item.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <item.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">{item.title}</h3>
                <p className="text-gray-600 text-sm">{item.description}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
