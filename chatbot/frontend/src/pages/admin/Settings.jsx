import { useEffect, useState } from 'react';
import { useAdminStore } from '../../store/useAdminStore';

export default function Settings() {
  const { mode, loading, error, refreshMode, toggleMode, clearError } = useAdminStore();
  const [switching, setSwitching] = useState(false);

  useEffect(() => {
    refreshMode();
  }, [refreshMode]);

  const handleToggle = async () => {
    try {
      setSwitching(true);
      await toggleMode();
    } catch (err) {
      console.error('Toggle error:', err);
    } finally {
      setSwitching(false);
    }
  };

  const isHumanMode = mode === 'HUMAN_ONLINE';

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800">Settings</h1>
          <p className="text-gray-600 mt-2">Configure chatbot behavior and preferences</p>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex justify-between items-center">
            <span className="text-red-700">{error}</span>
            <button onClick={clearError} className="text-red-500 hover:text-red-700">
              ✕
            </button>
          </div>
        )}

        {/* Chat Mode Settings */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Chat Mode Configuration</h2>
          </div>

          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900">Chat Mode</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Current mode: <span className="font-semibold">{mode || 'Loading...'}</span>
                </p>
              </div>
              <button
                onClick={handleToggle}
                disabled={loading || switching}
                className={`relative inline-flex h-10 w-20 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                  isHumanMode ? 'bg-yellow-500' : 'bg-green-500'
                } disabled:opacity-50`}
              >
                <span
                  className={`inline-block h-8 w-8 transform rounded-full bg-white transition-transform ${
                    isHumanMode ? 'translate-x-11' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* AI Only Mode */}
              <div
                className={`p-4 rounded-lg border-2 transition-all ${
                  !isHumanMode
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 bg-white'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">🤖</span>
                  <h4 className="font-semibold text-gray-900">AI Only Mode</h4>
                </div>
                <p className="text-sm text-gray-600">
                  All messages are automatically handled by the AI assistant.
                  Best for 24/7 automated support.
                </p>
                {!isHumanMode && (
                  <div className="mt-2">
                    <span className="inline-block px-2 py-1 text-xs font-medium text-green-700 bg-green-100 rounded">
                      ACTIVE
                    </span>
                  </div>
                )}
              </div>

              {/* Human Online Mode */}
              <div
                className={`p-4 rounded-lg border-2 transition-all ${
                  isHumanMode
                    ? 'border-yellow-500 bg-yellow-50'
                    : 'border-gray-200 bg-white'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">👤</span>
                  <h4 className="font-semibold text-gray-900">Human Online Mode</h4>
                </div>
                <p className="text-sm text-gray-600">
                  Messages are queued for human operators to respond.
                  Users will see a notice that they're chatting with a human.
                </p>
                {isHumanMode && (
                  <div className="mt-2">
                    <span className="inline-block px-2 py-1 text-xs font-medium text-yellow-700 bg-yellow-100 rounded">
                      ACTIVE
                    </span>
                  </div>
                )}
              </div>
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> Switching modes will immediately affect all active chat sessions.
                {switching && ' Switching mode...'}
              </p>
            </div>
          </div>
        </div>

        {/* Additional Settings (Future) */}
        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Additional Settings</h2>
          <p className="text-gray-500">More configuration options coming soon...</p>
        </div>
      </div>
    </div>
  );
}
