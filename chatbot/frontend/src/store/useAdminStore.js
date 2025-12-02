import { create } from 'zustand';
import { 
  getChatMode, 
  setChatMode, 
  getUsers, 
  getUserBySession, 
  getUserHistoryBySession, 
  getStatistics 
} from '../api/admin';
import { 
  listDocuments, 
  getDocumentStats, 
  uploadDocument, 
  deleteDocument 
} from '../api/documents';

export const useAdminStore = create((set, get) => ({
  mode: 'AI_ONLY',
  users: [],
  stats: {},
  documents: [],
  docStats: {},
  loading: false,
  error: null,

  refreshMode: async () => {
    try {
      const { mode } = await getChatMode();
      set({ mode });
    } catch (error) {
      set({ error: error.message });
    }
  },

  toggleMode: async () => {
    try {
      const current = get().mode;
      const next = current === 'AI_ONLY' ? 'HUMAN_ONLINE' : 'AI_ONLY';
      await setChatMode(next);
      set({ mode: next });
    } catch (error) {
      set({ error: error.message });
    }
  },

  loadUsers: async () => {
    try {
      set({ loading: true });
      const users = await getUsers();
      set({ users, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  loadUserDetail: async (sessionId) => {
    try {
      return await getUserBySession(sessionId);
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  loadUserHistory: async (sessionId) => {
    try {
      return await getUserHistoryBySession(sessionId);
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  loadDocuments: async () => {
    try {
      set({ loading: true });
      const documents = await listDocuments();
      set({ documents, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  loadDocStats: async () => {
    try {
      const docStats = await getDocumentStats();
      set({ docStats });
    } catch (error) {
      set({ error: error.message });
    }
  },

  uploadDoc: async (file) => {
    try {
      const result = await uploadDocument(file);
      // Reload documents after upload
      await get().loadDocuments();
      await get().loadDocStats();
      return result;
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  removeDoc: async (filename) => {
    try {
      await deleteDocument(filename);
      // Reload documents after delete
      await get().loadDocuments();
      await get().loadDocStats();
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  loadStatistics: async () => {
    try {
      set({ loading: true });
      const stats = await getStatistics();
      set({ stats, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  clearError: () => set({ error: null }),
}));
