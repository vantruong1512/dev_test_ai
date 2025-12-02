"""
Database Service - SQLite/PostgreSQL
Quản lý chat history, documents metadata, settings
"""
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatMode(str, Enum):
    """Chế độ chat"""
    AI_ONLY = "AI_ONLY"
    HUMAN_ONLINE = "HUMAN_ONLINE"

class DatabaseService:
    """
    Service quản lý database
    
    Tables:
    - chat_messages: Lịch sử chat
    - documents: Metadata tài liệu
    - settings: Cấu hình hệ thống
    - users: Thông tin khách hàng
    """
    
    def __init__(self, db_path: str = "./data/chatbot.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Để truy cập theo tên cột
        
        self._init_tables()
        logger.info(f"✅ Database khởi tạo: {self.db_path}")
    
    def _init_tables(self):
        """Khởi tạo các bảng"""
        cursor = self.conn.cursor()
        
        # Table: chat_messages (multi-channel)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                channel TEXT DEFAULT 'web',
                sender TEXT,
                text TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes separately
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session ON chat_messages(session_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created ON chat_messages(created_at)
        """)
        
        # Table: documents
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL UNIQUE,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                char_count INTEGER,
                extension TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table: settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table: users (lead collection) - MULTI-CHANNEL SUPPORT
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                channel TEXT DEFAULT 'web',
                name TEXT,
                email TEXT,
                phone TEXT,
                tags TEXT,
                notes TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table: chat_history (lịch sử chat riêng biệt)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT NOT NULL,
                message TEXT NOT NULL,
                reply TEXT,
                context_used TEXT,
                provider TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for chat_history
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_user_id ON chat_history(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_history(session_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_created ON chat_history(created_at)
        """)
        
        # Insert default settings
        cursor.execute("""
            INSERT OR IGNORE INTO settings (key, value) 
            VALUES ('chat_mode', 'AI_ONLY')
        """)
        
        self.conn.commit()
        logger.info("✅ Tables khởi tạo thành công")
    
    # ==================== CHAT MESSAGES ====================
    
    def get_current_timestamp(self) -> str:
        """Lấy timestamp hiện tại ở định dạng ISO"""
        return datetime.now().isoformat()
    
    def save_chat_message(
        self,
        session_id: str,
        user_message: Optional[str] = None,
        message: Optional[str] = None,
        bot_response: Optional[str] = None,
        context_used: Optional[str] = None,
        provider: Optional[str] = None,
        channel: str = "web",
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Lưu tin nhắn chat - Support cả web và multi-channel (FB, Zalo, Telegram)
        
        Parameters:
        - session_id: ID session
        - user_message: Tin nhắn từ user (web flow)
        - message: Tin nhắn (Facebook/multi-channel flow)
        - bot_response: Trả lời từ bot
        - context_used: Context từ RAG
        - provider: LLM provider (ollama, openai, etc)
        - channel: Kênh (web, facebook, zalo, telegram)
        - metadata: Extra data (psid, mid, etc)
        """
        cursor = self.conn.cursor()
        
        # Support both 'message' (Facebook) và 'user_message' (Web)
        text = message if message else user_message
        
        # Insert into chat_messages table (multi-channel)
        cursor.execute("""
            INSERT INTO chat_messages 
            (session_id, channel, sender, text, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, channel, "user", text, metadata))
        
        self.conn.commit()
        message_id = cursor.lastrowid
        
        logger.info(f"💾 Lưu chat message ID={message_id}, session={session_id}, channel={channel}")
        return message_id
    
    def save_ai_reply(
        self,
        session_id: str,
        reply_text: str,
        channel: str = "web",
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Lưu trả lời từ AI"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO chat_messages 
            (session_id, channel, sender, text, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, channel, "ai", reply_text, metadata))
        
        self.conn.commit()
        message_id = cursor.lastrowid
        
        logger.info(f"💾 Lưu AI reply ID={message_id}, session={session_id}, channel={channel}")
        return message_id
    
    def get_chat_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lấy lịch sử chat theo session"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM chat_messages
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (session_id, limit))
        
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_all_sessions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Lấy danh sách tất cả sessions"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                session_id,
                COUNT(*) as message_count,
                MAX(created_at) as last_message_at,
                MIN(created_at) as first_message_at
            FROM chat_messages
            GROUP BY session_id
            ORDER BY last_message_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    # ==================== DOCUMENTS ====================
    
    def save_document_metadata(
        self,
        filename: str,
        file_path: str,
        file_size: int,
        char_count: int,
        extension: str
    ) -> int:
        """Lưu metadata document"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO documents 
            (filename, file_path, file_size, char_count, extension, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (filename, file_path, file_size, char_count, extension))
        
        self.conn.commit()
        doc_id = cursor.lastrowid
        
        logger.info(f"📄 Lưu document metadata: {filename}")
        return doc_id
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Lấy danh sách tất cả documents"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM documents
            ORDER BY uploaded_at DESC
        """)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def delete_document(self, filename: str) -> bool:
        """Xóa document metadata"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            DELETE FROM documents WHERE filename = ?
        """, (filename,))
        
        self.conn.commit()
        
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f"🗑️ Xóa document: {filename}")
        
        return deleted
    
    # ==================== SETTINGS ====================
    
    def get_setting(self, key: str) -> Optional[str]:
        """Lấy giá trị setting"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT value FROM settings WHERE key = ?
        """, (key,))
        
        row = cursor.fetchone()
        return row['value'] if row else None
    
    def set_setting(self, key: str, value: str):
        """Cập nhật setting"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value))
        
        self.conn.commit()
        logger.info(f"⚙️ Cập nhật setting: {key} = {value}")
    
    def get_chat_mode(self) -> ChatMode:
        """Lấy chế độ chat hiện tại"""
        mode = self.get_setting('chat_mode')
        return ChatMode(mode) if mode else ChatMode.AI_ONLY
    
    def set_chat_mode(self, mode: ChatMode):
        """Đặt chế độ chat"""
        self.set_setting('chat_mode', mode.value)
    
    # ==================== USERS (Lead Collection) ====================
    
    def save_user_info(
        self,
        session_id: str,
        channel: str = "web",
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        metadata: Optional[str] = None
    ) -> int:
        """
        Lưu thông tin user - LUỒNG ĐỠN GIẢN:
        
        🔑 LUỒNG MỚI (Frontend tạo session_id mới mỗi lần LeadGate):
        - Frontend luôn tạo session_id mới khi submit LeadGate
        - Backend nhận session_id mới + email/phone → Chỉ INSERT user mới
        - Không merge với session/email/phone cũ
        
        ✅ VALIDATION: Email là bắt buộc
        
        📋 Nếu email tồn tại với session khác → Vẫn tạo user mới
           (Frontend đảm bảo session_id mới, DB cho phép email unique được "release")
        """
        cursor = self.conn.cursor()
        
        # 🔑 LUỒNG ĐỘI CHỈNH: Check session_id trước
        # Nếu session_id này tồn tại → Cập nhật (user cùng session gửi msg lại)
        # Nếu session_id mới → Tạo user mới
        
        cursor.execute("SELECT id FROM users WHERE session_id = ?", (session_id,))
        existing_session = cursor.fetchone()
        
        if existing_session:
            # ✅ Cùng session → UPDATE thông tin
            user_id = existing_session['id']
            logger.info(f"🔄 Session {session_id} đã tồn tại → UPDATE user_id={user_id}")
            
            cursor.execute("""
                UPDATE users SET
                    channel = ?,
                    name = COALESCE(?, name),
                    email = COALESCE(?, email),
                    phone = COALESCE(?, phone),
                    metadata = COALESCE(?, metadata),
                    updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (channel, name, email, phone, metadata, session_id))
            
            logger.info(f"✅ UPDATE user_id={user_id}, channel={channel}, email={email}")
        else:
            # ✨ SESSION MỚI → INSERT user mới
            # ⚠️ Email có thể trùng với user cũ (khác session) → không sao
            # Frontend đảm bảo session_id mới
            
            # ✨ INSERT user mới
            cursor.execute("""
                INSERT INTO users (session_id, channel, name, email, phone, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, channel, name, email, phone, metadata))
            user_id = cursor.lastrowid
            
            logger.info(f"✨ USER MỚI: user_id={user_id}, session={session_id}, channel={channel}, email={email}")
        
        self.conn.commit()
        return user_id
    
    
    def get_user_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin user theo session_id"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM users WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin user theo email"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM users WHERE email = ?
        """, (email,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """[NEW] Lấy thông tin user theo user_id (dùng để filter chat history)"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM users WHERE id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin user theo phone"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM users WHERE phone = ?
        """, (phone,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_users(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Lấy danh sách tất cả users từ cả web (users table) và multi-channel (chat_messages)
        Return format: {session_id, email, name, phone, channel, message_count, last_message}
        """
        cursor = self.conn.cursor()
        
        # 1. Lấy web users từ bảng users
        cursor.execute("""
            SELECT 
                u.session_id,
                u.email,
                u.name,
                u.phone,
                'web' as channel,
                COUNT(cm.id) as message_count,
                MAX(cm.created_at) as last_message
            FROM users u
            LEFT JOIN chat_messages cm ON u.session_id = cm.session_id
            GROUP BY u.session_id
        """)
        web_users = [dict(row) for row in cursor.fetchall()]
        
        # 2. Lấy multi-channel users từ chat_messages (fb_, zalo_, tg_)
        cursor.execute("""
            SELECT 
                session_id,
                NULL as email,
                NULL as name,
                NULL as phone,
                channel,
                COUNT(*) as message_count,
                MAX(created_at) as last_message
            FROM chat_messages
            WHERE session_id LIKE 'fb_%' 
               OR session_id LIKE 'zalo_%' 
               OR session_id LIKE 'tg_%'
            GROUP BY session_id
        """)
        multi_channel_users = [dict(row) for row in cursor.fetchall()]
        
        # 3. Merge và sort theo last_message
        all_users = web_users + multi_channel_users
        all_users.sort(key=lambda x: x.get('last_message', ''), reverse=True)
        
        return all_users[:limit]
    
    # ==================== CHAT HISTORY (New Table) ====================
    
    def save_chat_to_history(
        self,
        user_id: int,
        session_id: str,
        message: str,
        reply: Optional[str] = None,
        context_used: Optional[str] = None,
        provider: Optional[str] = None
    ) -> int:
        """Lưu chat vào bảng chat_history (liên kết với user_id)"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO chat_history 
            (user_id, session_id, message, reply, context_used, provider)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, session_id, message, reply, context_used, provider))
        
        self.conn.commit()
        chat_id = cursor.lastrowid
        
        logger.info(f"💾 Lưu chat history ID={chat_id}, user_id={user_id}")
        return chat_id
    
    def get_user_chat_history(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lấy lịch sử chat của user (theo user_id)"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM chat_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_chat_history_by_session(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lấy lịch sử chat theo session_id"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT ch.*, u.name, u.email, u.phone
            FROM chat_history ch
            LEFT JOIN users u ON ch.user_id = u.id
            WHERE ch.session_id = ?
            ORDER BY ch.created_at DESC
            LIMIT ?
        """, (session_id, limit))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_chat_history_by_email(
        self,
        email: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lấy lịch sử chat theo email"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT ch.*, u.name, u.email, u.phone
            FROM chat_history ch
            JOIN users u ON ch.user_id = u.id
            WHERE u.email = ?
            ORDER BY ch.created_at DESC
            LIMIT ?
        """, (email, limit))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    # ==================== STATISTICS ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Thống kê tổng quan"""
        cursor = self.conn.cursor()
        
        # Total messages
        cursor.execute("SELECT COUNT(*) as count FROM chat_messages")
        total_messages = cursor.fetchone()['count']
        
        # Total sessions
        cursor.execute("SELECT COUNT(DISTINCT session_id) as count FROM chat_messages")
        total_sessions = cursor.fetchone()['count']
        
        # Total documents
        cursor.execute("SELECT COUNT(*) as count FROM documents")
        total_documents = cursor.fetchone()['count']
        
        # Total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        # Chat mode
        chat_mode = self.get_chat_mode()
        
        return {
            'total_messages': total_messages,
            'total_sessions': total_sessions,
            'total_documents': total_documents,
            'total_users': total_users,
            'chat_mode': chat_mode.value
        }
    
    def close(self):
        """Đóng kết nối database"""
        self.conn.close()
        logger.info("🔒 Database connection closed")


# Singleton instance
_db_service = None

def get_db_service() -> DatabaseService:
    """Lấy database service instance (singleton)"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service


if __name__ == "__main__":
    print("🧪 Testing Database Service...\n")
    
    db = DatabaseService("./data/test_chatbot.db")
    
    # Test save chat message
    print("1️⃣ Testing save chat message...")
    msg_id = db.save_chat_message(
        session_id="test123",
        user_message="Xin chào",
        bot_response="Xin chào! Tôi có thể giúp gì cho bạn?",
        provider="ollama"
    )
    print(f"  Saved message ID: {msg_id}\n")
    
    # Test get chat history
    print("2️⃣ Testing get chat history...")
    history = db.get_chat_history("test123")
    print(f"  Found {len(history)} messages\n")
    
    # Test save user info
    print("3️⃣ Testing save user info...")
    user_id = db.save_user_info(
        session_id="test123",
        name="Nguyễn Văn A",
        email="test@example.com"
    )
    print(f"  Saved user ID: {user_id}\n")
    
    # Test settings
    print("4️⃣ Testing settings...")
    db.set_chat_mode(ChatMode.HUMAN_ONLINE)
    mode = db.get_chat_mode()
    print(f"  Chat mode: {mode.value}\n")
    
    # Test statistics
    print("5️⃣ Testing statistics...")
    stats = db.get_statistics()
    print(f"  Stats: {stats}\n")
    
    db.close()
    print("✅ All tests completed!")
