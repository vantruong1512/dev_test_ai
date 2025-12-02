import React, { useState } from 'react';
import { Upload } from 'lucide-react';

export default function FileUploader({ onUpload, loading = false, accept = '.pdf,.docx,.txt' }) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0 && onUpload) {
      onUpload(files[0]);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file && onUpload) {
      onUpload(file);
    }
    // Reset input
    e.target.value = '';
  };

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-8 text-center transition ${
        isDragging
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-300 hover:border-blue-500'
      } ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      <input
        type="file"
        id="file-upload"
        accept={accept}
        onChange={handleFileChange}
        disabled={loading}
        className="hidden"
      />
      <label
        htmlFor="file-upload"
        className={`flex flex-col items-center justify-center gap-2 ${
          loading ? 'cursor-not-allowed' : 'cursor-pointer'
        }`}
      >
        <Upload className="w-8 h-8 text-gray-400" />
        <div>
          <p className="text-blue-600 font-semibold hover:text-blue-700">
            {loading ? 'Đang upload...' : 'Chọn file hoặc kéo thả'}
          </p>
          <p className="text-sm text-gray-500 mt-1">
            Hỗ trợ: PDF, DOCX, TXT
          </p>
        </div>
      </label>
    </div>
  );
}

