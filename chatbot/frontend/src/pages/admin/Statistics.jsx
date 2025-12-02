import React, { useEffect } from 'react';
import { useAdminStore } from '../../store/useAdminStore';
import DataCard from '../../components/DataCard';
import Table from '../../components/Table';
import { Users, MessageSquare, FileText, Activity } from 'lucide-react';

export default function Statistics() {
  const { stats, loading, error, loadStatistics, clearError } = useAdminStore();

  useEffect(() => {
    loadStatistics();
  }, []);

  const topDocumentsColumns = [
    {
      header: 'STT',
      accessor: 'index',
      render: (row, idx) => idx + 1
    },
    {
      header: 'Tên tài liệu',
      accessor: 'filename'
    },
    {
      header: 'Lần sử dụng',
      accessor: 'used',
      render: (row) => (
        <span className="font-semibold text-blue-600">{row.used || 0}</span>
      )
    }
  ];

  const dailyMessagesColumns = [
    {
      header: 'Ngày',
      accessor: 'date'
    },
    {
      header: 'Số lượng',
      accessor: 'count',
      render: (row) => row.count || 0
    },
    {
      header: 'Biểu đồ',
      accessor: 'count',
      render: (row) => {
        const maxCount = stats?.daily_messages?.reduce((max, d) => Math.max(max, d.count || 0), 1) || 1;
        const percentage = ((row.count || 0) / maxCount) * 100;
        return (
          <div className="w-full h-6 bg-gray-200 rounded overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-400 to-blue-600 transition-all"
              style={{ width: `${percentage}%` }}
            />
          </div>
        );
      }
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Thống kê & Phân tích</h1>
          <p className="text-gray-600 mt-2">Tổng quan hiệu suất và sử dụng chatbot</p>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex justify-between items-center">
            <span className="text-red-700">{error}</span>
            <button 
              onClick={clearError} 
              className="text-red-500 hover:text-red-700 font-semibold"
            >
              ✕
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin w-8 h-8 border-2 border-gray-300 border-t-blue-600 rounded-full mx-auto mb-3"></div>
            <p className="text-gray-500">Đang tải thống kê...</p>
          </div>
        ) : (
          <>
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
              <DataCard
                title="Tổng Users"
                value={stats?.total_users || 0}
                icon={<Users className="w-6 h-6" />}
                color="blue"
              />
              <DataCard
                title="Tổng Messages"
                value={stats?.total_messages || 0}
                icon={<MessageSquare className="w-6 h-6" />}
                color="green"
              />
              <DataCard
                title="AI Messages"
                value={stats?.total_ai_messages || 0}
                icon={<Activity className="w-6 h-6" />}
                color="purple"
              />
              <DataCard
                title="Human Messages"
                value={stats?.total_human_messages || 0}
                icon={<MessageSquare className="w-6 h-6" />}
                color="yellow"
              />
              <DataCard
                title="Tài liệu"
                value={stats?.total_documents || 0}
                icon={<FileText className="w-6 h-6" />}
                color="red"
              />
            </div>

            {/* Active Sessions */}
            {stats?.active_sessions !== undefined && (
              <div className="mb-6">
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-2">Phiên hoạt động</h2>
                  <p className="text-4xl font-bold text-blue-600">{stats.active_sessions}</p>
                  <p className="text-sm text-gray-600 mt-2">Phiên chat đang mở</p>
                </div>
              </div>
            )}

            {/* Top Documents */}
            {stats?.top_documents && stats.top_documents.length > 0 && (
              <div className="mb-6">
                <div className="bg-white rounded-xl shadow-sm">
                  <div className="p-6 border-b border-gray-200">
                    <h2 className="text-lg font-semibold text-gray-900">Tài liệu được sử dụng nhiều</h2>
                  </div>
                  <Table
                    columns={topDocumentsColumns}
                    data={stats.top_documents.map((doc, idx) => ({ ...doc, index: idx }))}
                  />
                  {stats.top_documents.length === 0 && (
                    <div className="p-6 text-center text-gray-500">Chưa có dữ liệu</div>
                  )}
                </div>
              </div>
            )}

            {/* Daily Messages */}
            {stats?.daily_messages && stats.daily_messages.length > 0 && (
              <div>
                <div className="bg-white rounded-xl shadow-sm">
                  <div className="p-6 border-b border-gray-200">
                    <h2 className="text-lg font-semibold text-gray-900">Tin nhắn theo ngày</h2>
                  </div>
                  <Table
                    columns={dailyMessagesColumns}
                    data={stats.daily_messages}
                  />
                  {stats.daily_messages.length === 0 && (
                    <div className="p-6 text-center text-gray-500">Chưa có dữ liệu</div>
                  )}
                </div>
              </div>
            )}

            {/* Refresh Button */}
            <div className="mt-6 text-center">
              <button
                onClick={loadStatistics}
                disabled={loading}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50 transition"
              >
                {loading ? 'Đang tải...' : 'Tải lại'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
