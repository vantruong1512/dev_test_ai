import api from './axios';

export const listDocuments = () => 
  api.get('/admin/documents').then(r => r.data);

// Lấy thống kê tài liệu toàn bộ (không per-file)
export const getDocumentStats = () => 
  api.get('/admin/documents/stats').then(r => r.data);

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/admin/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const deleteDocument = (filename) => 
  api.delete(`/admin/documents/${encodeURIComponent(filename)}`).then(r => r.data);
