import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAdminStore } from '../../store/useAdminStore';
import MessageBubble from '../../components/MessageBubble';

export default function UserDetail() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const { loadUserDetail, loadUserHistory } = useAdminStore();
  const [userInfo, setUserInfo] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [user, historyResponse] = await Promise.all([
          loadUserDetail(sessionId),
          loadUserHistory(sessionId)
        ]);
        setUserInfo(user);
        // Extract the history array from the response object
        setHistory(historyResponse?.history || []);
      } catch (err) {
        setError(err.message || 'Failed to load user details');
      } finally {
        setLoading(false);
      }
    };

    if (sessionId) {
      fetchData();
    }
  }, [sessionId, loadUserDetail, loadUserHistory]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12 text-gray-500">Loading user details...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-red-700">
            {error}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <button
          onClick={() => navigate('/admin/users')}
          className="mb-4 px-4 py-2 text-blue-600 hover:text-blue-800 flex items-center gap-2"
        >
          ← Back to Users
        </button>

        <h1 className="text-3xl font-bold text-gray-800 mb-6">User Details</h1>

        {/* User Info Card */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">User Information</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Session ID</p>
              <p className="font-mono text-sm">{sessionId}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Email</p>
              <p className="font-medium">{userInfo?.email || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Name</p>
              <p className="font-medium">{userInfo?.name || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Phone</p>
              <p className="font-medium">{userInfo?.phone || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Messages</p>
              <p className="font-medium">{history.length}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Last Active</p>
              <p className="font-medium">
                {history.length > 0
                  ? new Date(history[history.length - 1].timestamp).toLocaleString('vi-VN')
                  : 'N/A'}
              </p>
            </div>
          </div>
        </div>

        {/* Chat History */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Chat History</h2>
          {history.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No messages yet</p>
          ) : (
            <div className="space-y-4 max-h-[600px] overflow-y-auto">
              {history.map((msg, idx) => (
                <MessageBubble key={idx} message={msg} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
