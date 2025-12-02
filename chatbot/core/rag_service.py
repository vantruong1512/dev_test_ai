"""
Vector RAG Service - ChromaDB + Embeddings
Sử dụng semantic search để tìm chunks liên quan, nhanh hơn full-file loading
"""
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    VECTOR_DB_AVAILABLE = True
except ImportError:
    VECTOR_DB_AVAILABLE = False
    logging.warning("⚠️ ChromaDB hoặc sentence-transformers chưa cài đặt")

# Document loaders
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorRAGService:
    """
    RAG Service với Vector Database
    
    Tính năng:
    - Chunk tài liệu thành đoạn nhỏ (500 chars)
    - Embed chunks bằng Vietnamese sentence transformer
    - Lưu vào ChromaDB
    - Semantic search: Tìm top-K chunks liên quan
    - Nhanh hơn 10x so với full-file loading
    """
    
    # Cấu hình chunking
    CHUNK_SIZE = 1000         # Tăng lên 1000 để bảng không bị chia nhỏ
    CHUNK_OVERLAP = 100       # Tăng overlap để đảm bảo thông tin liên tiếp
    TOP_K_CHUNKS = 20         # Tăng lên 20 để lấy đủ chunks liên quan
    MAX_CONTEXT_CHARS = 6000  # Tăng lên 6000 để chứa đủ thông tin chi tiết
    
    # Supported file extensions
    supported_extensions = {'.pdf', '.docx', '.txt', '.md'}  # .doc không hỗ trợ (Word 97-2003)
    
    def __init__(
        self, 
        uploads_dir: str = "./data/uploads",
        vector_db_dir: str = "./data/vector_db"
    ):
        if not VECTOR_DB_AVAILABLE:
            raise ImportError(
                "Cần cài đặt: pip install chromadb sentence-transformers"
            )
        
        self.uploads_dir = Path(uploads_dir)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        
        self.vector_db_dir = Path(vector_db_dir)
        self.vector_db_dir.mkdir(parents=True, exist_ok=True)
        
        # Khởi tạo ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.vector_db_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Collection name
        self.collection_name = "documents"
        
        # Lấy hoặc tạo collection
        try:
            self.collection = self.client.get_collection(self.collection_name)
            logger.info(f"✅ Đã load collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Document chunks with embeddings"}
            )
            logger.info(f"✅ Tạo collection mới: {self.collection_name}")
        
        # Khởi tạo embedding model (Vietnamese support)
        logger.info("🔄 Loading embedding model...")
        self.embedding_model = SentenceTransformer('keepitreal/vietnamese-sbert')
        logger.info("✅ Embedding model loaded")
        
        logger.info(f"✅ Vector RAG Service khởi tạo")
    
    def load_pdf_file(self, file_path: Path) -> str:
        """Load toàn bộ nội dung PDF"""
        try:
            loader = PyPDFLoader(str(file_path))
            documents = loader.load()
            full_content = "\n\n".join([doc.page_content for doc in documents])
            logger.info(f"✅ Load PDF: {file_path.name} - {len(full_content)} chars")
            return full_content
        except Exception as e:
            logger.error(f"❌ Lỗi load PDF {file_path}: {e}")
            return ""
    
    def load_docx_file(self, file_path: Path) -> str:
        """Load toàn bộ nội dung DOCX hoặc DOC"""
        try:
            # Thử với Docx2txtLoader (hỗ trợ .docx)
            loader = Docx2txtLoader(str(file_path))
            documents = loader.load()
            full_content = "\n\n".join([doc.page_content for doc in documents])
            logger.info(f"✅ Load DOCX: {file_path.name} - {len(full_content)} chars")
            return full_content
        except Exception as e:
            # Fallback: Thử với docx2txt library trực tiếp
            try:
                import docx2txt
                text = docx2txt.process(str(file_path))
                if text and text.strip():
                    logger.info(f"✅ Load DOC (fallback): {file_path.name} - {len(text)} chars")
                    return text
            except Exception as e2:
                logger.error(f"❌ Fallback cũng thất bại: {e2}")
            
            # Nếu vẫn lỗi, thông báo rõ ràng
            logger.error(f"❌ Lỗi load Word file {file_path}: {e}")
            logger.warning(f"⚠️ File .doc (Word 97-2003) không được hỗ trợ tốt. Vui lòng chuyển sang .docx (Word 2007+)")
            return ""
    
    def load_text_file(self, file_path: Path) -> str:
        """Load file text"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"❌ Lỗi load text {file_path}: {e}")
                return ""
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Chia text thành các chunks nhỏ với overlap
        
        Args:
            text: Văn bản cần chia
            chunk_size: Kích thước mỗi chunk (chars)
            overlap: Số ký tự overlap giữa các chunks
        
        Returns:
            List[str] - Danh sách chunks
        """
        chunk_size = chunk_size or self.CHUNK_SIZE
        overlap = overlap or self.CHUNK_OVERLAP
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Tìm dấu câu gần nhất để cắt tự nhiên
            if end < len(text):
                last_period = max(
                    chunk.rfind('.'),
                    chunk.rfind('!'),
                    chunk.rfind('?'),
                    chunk.rfind('\n')
                )
                if last_period > chunk_size * 0.7:  # Chỉ cắt nếu gần cuối
                    chunk = chunk[:last_period + 1]
                    end = start + last_period + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return [c for c in chunks if len(c) > 50]  # Bỏ chunks quá ngắn
    
    def index_document(self, file_path: Path) -> int:
        """
        Index một document vào vector DB
        
        Args:
            file_path: Đường dẫn file
        
        Returns:
            int - Số chunks đã index
        """
        ext = file_path.suffix.lower()
        
        # Load content
        if ext == '.pdf':
            content = self.load_pdf_file(file_path)
        elif ext in ['.docx', '.doc']:
            content = self.load_docx_file(file_path)
        elif ext in ['.txt', '.md']:
            content = self.load_text_file(file_path)
        else:
            logger.warning(f"⚠️ Không hỗ trợ: {ext}")
            return 0
        
        if not content:
            return 0
        
        # Chunk content
        chunks = self.chunk_text(content)
        logger.info(f"📄 {file_path.name}: {len(chunks)} chunks")
        
        # Prepare data cho ChromaDB
        chunk_ids = [f"{file_path.name}_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "filename": file_path.name,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "indexed_at": datetime.now().isoformat()
            }
            for i in range(len(chunks))
        ]
        
        # Embed và add vào collection
        embeddings = self.embedding_model.encode(chunks).tolist()
        
        self.collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        
        logger.info(f"✅ Indexed {len(chunks)} chunks từ {file_path.name}")
        return len(chunks)
    
    def index_all_documents(self, force_reindex: bool = False) -> Dict:
        """
        Index tất cả documents trong uploads_dir
        
        Args:
            force_reindex: Nếu True, xóa và index lại toàn bộ
        
        Returns:
            Dict với thống kê
        """
        if force_reindex:
            logger.info("🔄 Force reindex: Xóa collection cũ...")
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Document chunks with embeddings"}
            )
        
        total_files = 0
        total_chunks = 0
        
        supported_exts = {'.pdf', '.docx', '.doc', '.txt', '.md'}
        
        for file_path in self.uploads_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_exts:
                chunks = self.index_document(file_path)
                if chunks > 0:
                    total_files += 1
                    total_chunks += chunks
        
        stats = {
            'total_files': total_files,
            'total_chunks': total_chunks,
            'collection_size': self.collection.count()
        }
        
        logger.info(f"📊 Index complete: {total_files} files, {total_chunks} chunks")
        return stats
    
    def search_relevant_chunks(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Tìm kiếm chunks liên quan đến query bằng semantic search
        
        Args:
            query: Câu hỏi của user
            top_k: Số chunks lấy ra (default: TOP_K_CHUNKS)
        
        Returns:
            List[Dict] với keys: text, metadata, distance
        """
        top_k = top_k or self.TOP_K_CHUNKS
        
        # Embed query
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Search trong ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        chunks = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                chunks.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })
        
        logger.info(f"🔍 Tìm thấy {len(chunks)} chunks liên quan")
        return chunks
    
    def build_context(self, query: str, max_chars: int = None) -> str:
        """
        Xây dựng context từ relevant chunks (từ nhiều file khác nhau)
        
        Args:
            query: Câu hỏi user
            max_chars: Giới hạn tổng chars (default: MAX_CONTEXT_CHARS)
        
        Returns:
            str - Context đã format
        """
        max_chars = max_chars or self.MAX_CONTEXT_CHARS
        
        # Tìm chunks liên quan
        chunks = self.search_relevant_chunks(query, top_k=self.TOP_K_CHUNKS)
        
        if not chunks:
            logger.warning("⚠️ Không tìm thấy chunks liên quan")
            return ""
        
        # Nhóm chunks theo file để đảm bảo lấy từ nhiều file
        files_chunks = {}
        for chunk in chunks:
            filename = chunk['metadata']['filename']
            if filename not in files_chunks:
                files_chunks[filename] = []
            files_chunks[filename].append(chunk)
        
        logger.info(f"📚 Tìm thấy chunks từ {len(files_chunks)} file: {list(files_chunks.keys())}")
        
        # Lọc file theo từ khóa trong câu hỏi
        query_lower = query.lower()
        target_files = []
        
        # Tìm file cụ thể
        if 'automation' in query_lower:
            for fname in files_chunks.keys():
                if 'automation' in fname.lower():
                    target_files = [fname]
                    break
        elif 'quản trị' in query_lower:
            for fname in files_chunks.keys():
                if 'quan tri' in fname.lower():
                    target_files = [fname]
                    break
        elif 'ai' in query_lower or 'trí tuệ' in query_lower:
            # Câu hỏi về AI - Bỏ điều kiện length
            for fname in files_chunks.keys():
                if 'ai engineer' in fname.lower() or 'tri tue' in fname.lower():
                    target_files = [fname]
                    break
        
        # Câu hỏi CHUNG → lấy TẤT CẢ
        if not target_files:
            target_files = list(files_chunks.keys())
            logger.info(f"🎯 Chung → {len(target_files)} khóa")
        else:
            logger.info(f"🎯 Cụ thể: {target_files[0]}")
        
        # Build context từ chunks liên quan
        context_parts = []
        total_chars = 0
        
        for fname in target_files:
            if fname not in files_chunks:
                continue
            
            # Header file
            header = f"\n=== {fname.replace('.pdf', '').replace('.docx', '')} ===\n"
            if total_chars + len(header) > max_chars:
                break
            
            context_parts.append(header)
            total_chars += len(header)
            
            # Lấy TẤT CẢ chunks từ file này cho đến khi hết quota
            # Các chunks đã được sắp xếp theo distance (gần nhất trước)
            for chunk in files_chunks[fname]:
                text = chunk['text']
                
                # Kiểm tra xem còn đủ quota không
                if total_chars + len(text) + 2 > max_chars:  # +2 cho newline
                    break
                
                # Thêm chunk vào context
                context_parts.append(text)
                context_parts.append("\n")  # Ngăn cách giữa các chunks
                total_chars += len(text) + 2
        
        final_context = "\n".join(context_parts)
        logger.info(f"✅ Context: {len(final_context)} chars")
        
        return final_context
    
    def load_single_file(self, file_path: Path) -> Optional[Dict]:
        """
        Load một file và trả về metadata (cho upload endpoint)
        
        Args:
            file_path: Path đến file cần load
            
        Returns:
            Dict với metadata hoặc None nếu lỗi
        """
        try:
            file_ext = file_path.suffix.lower()
            
            # Load content
            if file_ext == '.pdf':
                content = self.load_pdf_file(file_path)
            elif file_ext in ['.docx', '.doc']:
                content = self.load_docx_file(file_path)
            elif file_ext in ['.txt', '.md']:
                content = self.load_text_file(file_path)
            else:
                logger.warning(f"⚠️ Unsupported file type: {file_ext}")
                return None
            
            if not content:
                return None
            
            # Index luôn vào vector DB
            chunks_count = self.index_document(file_path)
            
            return {
                'filename': file_path.name,
                'size': file_path.stat().st_size,
                'char_count': len(content),
                'extension': file_ext,
                'chunks_indexed': chunks_count
            }
            
        except Exception as e:
            logger.error(f"❌ Lỗi load file {file_path}: {e}")
            return None
    
    def get_document_stats(self) -> Dict:
        """
        Thống kê documents (cho admin endpoint)
        
        Returns:
            Dict với thống kê
        """
        try:
            # Đếm số files trong uploads_dir
            files = list(self.uploads_dir.glob('*'))
            pdf_files = [f for f in files if f.suffix.lower() == '.pdf']
            docx_files = [f for f in files if f.suffix.lower() in ['.docx', '.doc']]
            txt_files = [f for f in files if f.suffix.lower() in ['.txt', '.md']]
            
            # Thống kê vector DB
            vector_stats = self.get_statistics()
            
            return {
                'total_files': len(files),
                'pdf_count': len(pdf_files),
                'docx_count': len(docx_files),
                'txt_count': len(txt_files),
                'vector_db': vector_stats
            }
            
        except Exception as e:
            logger.error(f"❌ Lỗi get document stats: {e}")
            return {
                'total_files': 0,
                'pdf_count': 0,
                'docx_count': 0,
                'txt_count': 0,
                'vector_db': {}
            }
    
    def get_statistics(self) -> Dict:
        """Thống kê vector DB"""
        count = self.collection.count()
        
        # Lấy sample metadata
        sample = self.collection.get(limit=1)
        
        return {
            'total_chunks': count,
            'collection_name': self.collection_name,
            'chunk_size': self.CHUNK_SIZE,
            'top_k': self.TOP_K_CHUNKS,
            'max_context_chars': self.MAX_CONTEXT_CHARS,
            'sample_metadata': sample['metadatas'][0] if sample['metadatas'] else None
        }


# Singleton instance
_rag_service = None

def get_rag_service() -> VectorRAGService:
    """Lấy RAG service instance (singleton)"""
    global _rag_service
    if _rag_service is None:
        _rag_service = VectorRAGService()
    return _rag_service


if __name__ == "__main__":
    import asyncio
    
    print("🧪 Testing Vector RAG Service...\n")
    
    # Khởi tạo service
    rag = VectorRAGService()
    
    # Index documents
    print("📚 Indexing documents...")
    stats = rag.index_all_documents(force_reindex=True)
    print(f"✅ Indexed: {stats}\n")
    
    # Test search
    query = "học phí bao nhiêu?"
    print(f"🔍 Query: {query}")
    
    chunks = rag.search_relevant_chunks(query, top_k=3)
    print(f"📊 Found {len(chunks)} chunks:\n")
    
    for i, chunk in enumerate(chunks, 1):
        print(f"{i}. {chunk['metadata']['filename']}")
        print(f"   Text: {chunk['text'][:100]}...")
        print(f"   Distance: {chunk['distance']:.4f}\n")
    
    # Build context
    context = rag.build_context(query)
    print(f"✅ Context length: {len(context)} chars")
    print(f"Context preview:\n{context[:500]}...")
