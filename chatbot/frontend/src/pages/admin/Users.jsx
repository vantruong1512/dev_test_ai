import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAdminStore } from '../../store/useAdminStore';
import Table from '../../components/Table';

// Channel icons
const CHANNEL_INFO = {
  web: { icon: '🌐', label: 'Web', color: 'blue' },
  facebook: { icon: '📱', label: 'Facebook', color: 'indigo' },
  zalo: { icon: '💬', label: 'Zalo', color: 'cyan' },
  telegram: { icon: '✈️', label: 'Telegram', color: 'sky' }
};

export default function Users() {
  const navigate = useNavigate();
  const { users, loading, error, loadUsers, clearError } = useAdminStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterChannel, setFilterChannel] = useState('all');

  useEffect(() => {
    loadUsers();
  }, []);

  // Ensure users is array
  const usersList = Array.isArray(users) ? users : [];
  
  // Filter users by email/phone/name and channel
  const filteredUsers = usersList.filter(user => {
    // Channel filter
    if (filterChannel !== 'all' && (user.channel || 'web') !== filterChannel) {
      return false;
    }
    
    // Search filter
    const term = searchTerm.toLowerCase();
    return (
      (user.email?.toLowerCase() || '').includes(term) ||
      (user.phone?.toLowerCase() || '').includes(term) ||
      (user.name?.toLowerCase() || '').includes(term)
    );
  });

  const columns = [
    { 
      header: 'STT', 
      accessor: 'index',
      render: (row, idx) => idx + 1 
    },
    { 
      header: 'Channel', 
      accessor: 'channel',
      render: (row) => {
        const channel = row.channel || 'web';
        const info = CHANNEL_INFO[channel];
        return (
          <div className="flex items-center gap-2">
            <span className="text-lg">{info?.icon}</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium bg-${info?.color}-100 text-${info?.color}-700`}>
              {info?.label}
            </span>
          </div>
        );
      }
    },
    { 
      header: 'Email', 
      accessor: 'email',
      render: (row) => row.email || 'N/A'
    },
    { 
      header: 'Name', 
      accessor: 'name',
      render: (row) => row.name || 'N/A' 
    },
    { 
      header: 'Phone', 
      accessor: 'phone',
      render: (row) => row.phone || 'N/A' 
    },
    { 
      header: 'Messages', 
      accessor: 'message_count',
      render: (row) => row.message_count || 0 
    }
  ];

  const handleRowClick = (user) => {
    navigate(`/admin/users/${user.session_id}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Quản lý Users</h1>
          <p className="text-gray-600 mt-2">Xem danh sách tất cả người dùng từ các kênh</p>
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

        {/* Main Card */}
        <div className="bg-white rounded-xl shadow-sm">
          {/* Toolbar */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex flex-col gap-4">
              {/* Search + Reload */}
              <div className="flex flex-col gap-4 md:flex-row md:justify-between md:items-center">
                <div className="flex-1">
                  <input
                    type="text"
                    placeholder="Tìm kiếm email, phone, name..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <button
                  onClick={loadUsers}
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
                >
                  {loading ? 'Đang tải...' : 'Tải lại'}
                </button>
              </div>

              {/* Channel Filter */}
              <div className="flex gap-2 flex-wrap">
                <span className="text-sm font-medium text-gray-700 flex items-center">Lọc kênh:</span>
                <button
                  onClick={() => setFilterChannel('all')}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    filterChannel === 'all'
                      ? 'bg-gray-900 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Tất cả
                </button>
                {Object.entries(CHANNEL_INFO).map(([key, info]) => (
                  <button
                    key={key}
                    onClick={() => setFilterChannel(key)}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors flex items-center gap-1 ${
                      filterChannel === key
                        ? `bg-${info.color}-600 text-white`
                        : `bg-${info.color}-100 text-${info.color}-700 hover:bg-${info.color}-200`
                    }`}
                  >
                    <span>{info.icon}</span>
                    {info.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Table or Empty/Loading State */}
          {loading ? (
            <div className="p-12 text-center text-gray-500">
              <div className="spinner inline-block w-6 h-6 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
              <p className="mt-3">Đang tải dữ liệu...</p>
            </div>
          ) : filteredUsers.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <p className="text-lg font-medium">
                {usersList.length === 0 ? 'Không có người dùng nào' : 'Không tìm thấy kết quả'}
              </p>
            </div>
          ) : (
            <Table
              columns={columns}
              data={filteredUsers.map((user, idx) => ({ ...user, index: idx }))}
              onRowClick={handleRowClick}
            />
          )}

          {/* Footer Stats */}
          <div className="p-6 border-t border-gray-200 bg-gray-50 rounded-b-xl">
            <p className="text-sm text-gray-600">
              Tổng cộng: <span className="font-semibold text-gray-900">{filteredUsers.length}</span> người dùng
              {filterChannel !== 'all' && ` (${CHANNEL_INFO[filterChannel]?.label})`}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
