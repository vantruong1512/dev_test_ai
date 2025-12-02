"""
LLM Service - Ollama Integration with Anti-Hallucination
Tích hợp Ollama với prompt engineering để chống bịa đặt thông tin
"""
import os
import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    """
    Service quản lý LLM với các tính năng:
    - Tích hợp Ollama (primary)
    - Fallback to cloud providers (Groq, DeepSeek)
    - Prompt engineering chống hallucination
    - Retry logic và error handling
    """
    
    def __init__(
        self,
        provider: str = "ollama",
        ollama_host: str = "http://127.0.0.1:11434",
        ollama_model: str = "qwen3:4b",
        timeout: int = 120
    ):
        self.provider = provider
        self.ollama_host = ollama_host
        self.ollama_model = ollama_model
        self.timeout = timeout
        
        # API keys cho cloud providers
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
        
        logger.info(f"✅ LLM Service khởi tạo - Provider: {provider}, Model: {ollama_model}")
    
    def build_anti_hallucination_prompt(self, context: str, user_question: str) -> str:
        """
        Xây dựng prompt chống hallucination - BẮT BUỘC trích dẫn chính xác từ context
        """
        
        prompt = f"""Bạn là trợ lý AI hỗ trợ khách hàng thân thiện và chính xác.

QUY TẮC QUAN TRỌNG:
1. ✅ CHỈ sử dụng thông tin từ NGỮ CẢNH bên dưới
2. ✅ Trích dẫn CHÍNH XÁC số liệu, giá cả, công thức từ ngữ cảnh (bao gồm cả phép tính nếu có)
3. ✅ Trả lời thân thiện, dễ hiểu và đầy đủ
4. ❌ KHÔNG tự bịa thêm thông tin không có trong ngữ cảnh
5. ✅ Nếu ngữ cảnh KHÔNG ĐỦ thông tin → Nói rõ và gợi ý liên hệ trực tiếp

VÍ DỤ TỐT:
- Câu hỏi: "Học phí AI bao nhiêu?"
- Ngữ cảnh có: "Học phí đóng theo tháng 3,000,000 VND * 6"
- Trả lời: "Học phí khóa AI có các gói sau:
  • Đóng theo tháng: 3,000,000 VND/tháng x 6 tháng
  • Đóng theo kỳ: 8,600,000 VND x 2 kỳ (tiết kiệm 5%)
  • Trọn gói: 16,200,000 VND (tiết kiệm 10%)"

NGỮ CẢNH:
{context}

CÂU HỎI: {user_question}

TRẢ LỜI (dựa trên ngữ cảnh, thân thiện và đầy đủ):"""
        return prompt
    
    async def generate_ollama(self, prompt: str) -> Optional[str]:
        """
        Gọi Ollama API để generate response
        
        Returns:
            str - Response từ LLM
            None - Nếu có lỗi
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Giảm xuống 0.1 để chống hallucination
                        "top_p": 0.8,
                        "top_k": 20,
                        "num_predict": 500,
                    }
                }
                
                logger.info(f"🤖 Gọi Ollama: {self.ollama_host}/api/generate")
                
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("response", "").strip()
                    
                    logger.info(f"✅ Ollama response: {len(answer)} chars")
                    return answer
                else:
                    logger.error(f"❌ Ollama error: {response.status_code} - {response.text}")
                    return None
        
        except httpx.ReadTimeout:
            logger.error(f"⏰ Ollama timeout sau {self.timeout}s")
            return None
        except Exception as e:
            logger.error(f"❌ Lỗi gọi Ollama: {e}")
            return None
    
    async def generate_groq(self, prompt: str) -> Optional[str]:
        """Fallback: Gọi Groq API"""
        if not self.groq_api_key:
            logger.warning("⚠️ Groq API key không có sẵn")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "llama3-70b-8192",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500
                }
                
                logger.info("🤖 Fallback to Groq...")
                
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result["choices"][0]["message"]["content"].strip()
                    logger.info(f"✅ Groq response: {len(answer)} chars")
                    return answer
                else:
                    logger.error(f"❌ Groq error: {response.status_code}")
                    return None
        
        except Exception as e:
            logger.error(f"❌ Lỗi gọi Groq: {e}")
            return None
    
    async def generate_with_context(
        self,
        user_question: str,
        context: str,
        retry: int = 2
    ) -> Dict[str, Any]:
        """
        Generate response với context và retry logic
        
        Args:
            user_question: Câu hỏi của user
            context: Context từ RAG
            retry: Số lần retry nếu fail
        
        Returns:
            {
                'success': bool,
                'answer': str,
                'provider': str,
                'error': Optional[str]
            }
        """
        # Xây dựng prompt chống hallucination
        prompt = self.build_anti_hallucination_prompt(context, user_question)
        
        # Log để debug
        logger.info(f"📝 Prompt length: {len(prompt)} chars")
        logger.info(f"❓ User question: {user_question}")
        
        # Thử các provider theo thứ tự
        providers = [
            ("ollama", self.generate_ollama),
            ("groq", self.generate_groq)
        ]
        
        for attempt in range(retry):
            for provider_name, generate_func in providers:
                try:
                    answer = await generate_func(prompt)
                    
                    if answer:
                        # Kiểm tra câu trả lời có hợp lý không
                        if len(answer) < 10:
                            logger.warning(f"⚠️ Câu trả lời quá ngắn: {answer}")
                            continue
                        
                        return {
                            'success': True,
                            'answer': answer,
                            'provider': provider_name,
                            'error': None
                        }
                
                except Exception as e:
                    logger.error(f"❌ Error with {provider_name}: {e}")
                    continue
            
            if attempt < retry - 1:
                logger.info(f"🔄 Retry attempt {attempt + 2}/{retry}")
        
        # Tất cả providers đều fail
        return {
            'success': False,
            'answer': "Xin lỗi, hệ thống AI tạm thời không phản hồi. Vui lòng thử lại sau hoặc liên hệ nhân viên hỗ trợ.",
            'provider': None,
            'error': "All providers failed"
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test kết nối với LLM provider"""
        try:
            test_prompt = "Hello, this is a test. Please respond with 'OK'."
            
            if self.provider == "ollama":
                response = await self.generate_ollama(test_prompt)
            else:
                response = await self.generate_groq(test_prompt)
            
            if response:
                return {
                    'status': 'ok',
                    'provider': self.provider,
                    'model': self.ollama_model,
                    'test_response': response
                }
            else:
                return {
                    'status': 'error',
                    'provider': self.provider,
                    'error': 'No response'
                }
        
        except Exception as e:
            return {
                'status': 'error',
                'provider': self.provider,
                'error': str(e)
            }


# Singleton instance
_llm_service = None

def get_llm_service() -> LLMService:
    """Lấy LLM service instance (singleton)"""
    global _llm_service
    if _llm_service is None:
        provider = os.getenv("LLM_PROVIDER", "ollama")
        ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "mistral")
        timeout = int(os.getenv("LLM_TIMEOUT_SECONDS", "120"))
        
        _llm_service = LLMService(
            provider=provider,
            ollama_host=ollama_host,
            ollama_model=ollama_model,
            timeout=timeout
        )
    return _llm_service


if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("🧪 Testing LLM Service...\n")
        
        llm = LLMService()
        
        # Test connection
        print("1️⃣ Testing connection...")
        test_result = await llm.test_connection()
        print(f"  Result: {test_result}\n")
        
        # Test with context
        print("2️⃣ Testing with context...")
        
        context = """
        Sản phẩm ABC có giá 1.000.000 VNĐ.
        Tính năng: Tăng hiệu suất 50%, tiết kiệm 30% chi phí.
        Liên hệ: support@example.com
        """
        
        question = "Sản phẩm ABC giá bao nhiêu?"
        
        result = await llm.generate_with_context(question, context)
        
        print(f"  Success: {result['success']}")
        print(f"  Provider: {result['provider']}")
        print(f"  Answer: {result['answer']}\n")
    
    asyncio.run(test())
