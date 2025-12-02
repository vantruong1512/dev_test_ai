import React, { useEffect, useState } from 'react';
import { useAdminStore } from '../../store/useAdminStore';
import FileUploader from '../../components/FileUploader';
import Table from '../../components/Table';
import DataCard from '../../components/DataCard';
import { FileText, Trash2 } from 'lucide-react';

export default function Documents() {
  const { documents, docStats, loading, error, loadDocuments, loadDocStats, uploadDoc, removeDoc, clearError } = useAdminStore();
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    loadDocuments();
    loadDocStats();
  }, []);

  const handleFileUpload = async (file) => {
    if (!file) return;

    try {
      setUploading(true);
      console.log('📤 Uploading file:', file.name);
      await uploadDoc(file);
      console.log('✅ Upload success, reloading...');
      await loadDocuments();
      await loadDocStats();
      setSelectedFile(null);
    } catch (err) {
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (filename) => {
    if (!confirm(`Bạn có chắc chắn muốn xóa "${filename}"?`)) return;

    try {
      console.log('🗑️ Deleting file:', filename);
      await removeDoc(filename);
      console.log('✅ Delete success, reloading...');
      await loadDocuments();
      await loadDocStats();
      if (selectedFile?.filename === filename) {
        setSelectedFile(null);
      }
    } catch (err) {
      console.error('Delete error:', err);
    }
  };

  const columns = [
    {
      header: 'Tên File',
      accessor: 'filename',
      render: (row) => (
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-blue-500" />
          <span>{row.filename}</span>
        </div>
      )
    },
    {
      header: 'Dung lượng',
      accessor: 'file_size',
      render: (row) => {
        const size = row.file_size || 0;
        if (size > 1024 * 1024) {
          return `${(size / (1024 * 1024)).toFixed(2)} MB`;
        }
        return `${(size / 1024).toFixed(2)} KB`;
      }
    },
    {
      header: 'Ký tự',
      accessor: 'char_count',
      render: (row) => (row.char_count || 0).toLocaleString()
    },
    {
      header: 'Loại',
      accessor: 'extension',
      render: (row) => (
        <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
          {row.extension || 'N/A'}
        </span>
      )
    },
    {
      header: 'Upload lúc',
      accessor: 'uploaded_at',
      render: (row) => {
        if (!row.uploaded_at) return 'N/A';
        return new Date(row.uploaded_at).toLocaleDateString('vi-VN');
      }
    },
    {
      header: 'Hành động',
      accessor: 'filename',
      render: (row) => (
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleDelete(row.filename);
          }}
          className="px-3 py-1 bg-red-500 hover:bg-red-600 text-white text-sm rounded-lg transition flex items-center gap-1"
        >
          <Trash2 className="w-4 h-4" />
          Xóa
        </button>
      )
    }
  ];

  const handleRowClick = (doc) => {
    setSelectedFile(doc);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Quản lý Tài liệu</h1>
          <p className="text-gray-600 mt-2">Upload và quản lý tài liệu cho RAG</p>
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

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <DataCard
            title="Tổng tài liệu"
            value={documents?.length || 0}
            icon={<FileText />}
            color="blue"
          />
          <DataCard
            title="Tổng dung lượng"
            value={docStats?.total_size ? `${(docStats.total_size / (1024 * 1024)).toFixed(2)} MB` : '0 MB'}
            icon={<FileText />}
            color="green"
          />
          <DataCard
            title="Tổng chunks"
            value={docStats?.total_chunks || 0}
            icon={<FileText />}
            color="yellow"
          />
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Upload + Table */}
          <div className="lg:col-span-2 space-y-6">
            {/* Upload Section */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload Tài liệu Mới</h2>
              <FileUploader
                onUpload={handleFileUpload}
                loading={uploading}
                accept=".pdf,.docx,.txt,.md"
              />
              {uploading && (
                <div className="mt-3 flex items-center gap-2 text-blue-600">
                  <div className="animate-spin w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                  <span>Đang upload...</span>
                </div>
              )}
            </div>

            {/* Documents Table */}
            <div className="bg-white rounded-xl shadow-sm">
              <div className="p-6 border-b border-gray-200">
                <div className="flex justify-between items-center">
                  <h2 className="text-lg font-semibold text-gray-900">Danh sách Tài liệu</h2>
                  <button
                    onClick={() => {
                      loadDocuments();
                      loadDocStats();
                    }}
                    disabled={loading}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50 transition"
                  >
                    {loading ? 'Đang tải...' : 'Tải lại'}
                  </button>
                </div>
              </div>

              {loading ? (
                <div className="p-12 text-center text-gray-500">
                  <div className="animate-spin w-6 h-6 border-2 border-gray-300 border-t-blue-600 rounded-full mx-auto mb-2"></div>
                  Đang tải danh sách...
                </div>
              ) : documents?.length === 0 ? (
                <div className="p-12 text-center text-gray-500">
                  Chưa có tài liệu nào
                </div>
              ) : (
                <Table
                  columns={columns}
                  data={documents}
                  onRowClick={handleRowClick}
                />
              )}

              {documents?.length > 0 && (
                <div className="p-4 bg-gray-50 border-t border-gray-200 text-sm text-gray-600">
                  Tổng cộng: <span className="font-semibold">{documents.length}</span> tài liệu
                </div>
              )}
            </div>
          </div>

          {/* Right: File Stats */}
          <div className="lg:col-span-1">
            {selectedFile ? (
              <div className="bg-white rounded-xl shadow-sm p-6 sticky top-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Chi tiết Tài liệu</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="text-sm text-gray-600">Tên file</label>
                    <p className="font-semibold text-gray-900 break-all">{selectedFile.filename}</p>
                  </div>

                  <div>
                    <label className="text-sm text-gray-600">Loại</label>
                    <p className="font-semibold text-gray-900">{selectedFile.extension || 'N/A'}</p>
                  </div>

                  <div>
                    <label className="text-sm text-gray-600">Dung lượng</label>
                    <p className="font-semibold text-gray-900">
                      {selectedFile.file_size ? `${(selectedFile.file_size / 1024).toFixed(2)} KB` : 'N/A'}
                    </p>
                  </div>

                  <div>
                    <label className="text-sm text-gray-600">Số ký tự</label>
                    <p className="font-semibold text-gray-900">
                      {selectedFile.char_count ? selectedFile.char_count.toLocaleString() : 'N/A'}
                    </p>
                  </div>

                  <div>
                    <label className="text-sm text-gray-600">Upload lúc</label>
                    <p className="font-semibold text-gray-900">
                      {selectedFile.uploaded_at 
                        ? new Date(selectedFile.uploaded_at).toLocaleString('vi-VN')
                        : 'N/A'}
                    </p>
                  </div>

                  <hr className="my-4" />

                  <div className="space-y-3">
                    <h4 className="font-semibold text-gray-900">Thống kê RAG</h4>
                    <div>
                      <label className="text-sm text-gray-600">Total chunks</label>
                      <p className="font-semibold text-gray-900">{docStats?.total_chunks || 0}</p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-600">Embedding dim</label>
                      <p className="font-semibold text-gray-900">{docStats?.embedding_dim || 'N/A'}</p>
                    </div>
                  </div>

                  <button
                    onClick={() => handleDelete(selectedFile.filename)}
                    className="w-full mt-4 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition"
                  >
                    Xóa tài liệu
                  </button>
                </div>
              </div>
            ) : (
              <div className="bg-gray-50 rounded-xl p-6 text-center text-gray-500">
                Chọn tài liệu để xem chi tiết
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
