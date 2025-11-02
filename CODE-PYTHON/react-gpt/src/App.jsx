import OpenAI from "openai";
import { useState, useEffect, useRef } from "react";

// Kiểm tra xem tin nhắn có phải là của bot không
function isBotMessage(chatMessage) {
  return chatMessage.role === "assistant";
}

function App() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [apiKey, setApiKey] = useState("");
  const [isKeySet, setIsKeySet] = useState(false);
  const [openai, setOpenai] = useState(null);
  const chatEndRef = useRef(null);

  // Load API key từ localStorage khi component mount
  useEffect(() => {
    const savedKey = localStorage.getItem("openai_api_key");
    if (savedKey) {
      setApiKey(savedKey);
      setIsKeySet(true);
      initializeOpenAI(savedKey);
    }
  }, []);

  // Auto scroll xuống cuối khi có tin nhắn mới
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  // Khởi tạo OpenAI instance
  const initializeOpenAI = (key) => {
    const openaiInstance = new OpenAI({
      apiKey: key,
      dangerouslyAllowBrowser: true,
    });
    setOpenai(openaiInstance);
  };

  // Xử lý khi người dùng nhập API key
  const handleSetApiKey = (e) => {
    e.preventDefault();
    if (apiKey.trim()) {
      localStorage.setItem("openai_api_key", apiKey);
      setIsKeySet(true);
      initializeOpenAI(apiKey);
    }
  };

  // Xử lý clear API key
  const handleClearKey = () => {
    localStorage.removeItem("openai_api_key");
    setApiKey("");
    setIsKeySet(false);
    setOpenai(null);
    setChatHistory([]);
  };

  // Xử lý clear chat history
  const handleClearChat = () => {
    setChatHistory([]);
  };

  // Gọi hàm này khi người dùng bấm enter, gửi tin nhắn
  const submitForm = async (e) => {
    e.preventDefault();
    
    if (!message.trim() || !openai) return;

    // Clear message ban đầu
    const currentMessage = message;
    setMessage("");

    // Thêm tin nhắn người dùng và tin nhắn "đang chờ" vào danh sách
    const userMessage = { role: "user", content: currentMessage };
    const waitingBotMessage = {
      role: "assistant",
      content: "Vui lòng chờ bot trả lời...",
    };
    
    const newHistory = [...chatHistory, userMessage, waitingBotMessage];
    setChatHistory(newHistory);

    try {
      // Gọi OpenAI API để lấy kết quả
      const chatCompletion = await openai.chat.completions.create({
        messages: [...chatHistory, userMessage],
        model: "gpt-4o-mini",
      });

      // Lấy tin nhắn của bot từ response, hiển thị cho người dùng
      const response = chatCompletion.choices[0].message.content;
      const botMessage = { role: "assistant", content: response };
      
      // Update history với tin nhắn thật từ bot (thay thế tin nhắn "đang chờ")
      setChatHistory([...chatHistory, userMessage, botMessage]);
    } catch (error) {
      // Xử lý lỗi
      const errorMessage = {
        role: "assistant",
        content: `Lỗi: ${error.message}. Vui lòng kiểm tra API key hoặc kết nối mạng.`,
      };
      setChatHistory([...chatHistory, userMessage, errorMessage]);
    }
  };

  // Nếu chưa có API key, hiển thị form nhập key
  if (!isKeySet) {
    return (
      <div className="bg-gray-100 h-screen flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
          <h1 className="text-2xl font-bold mb-4 text-center">
            ChatGPT React App
          </h1>
          <p className="text-gray-600 mb-4 text-sm">
            Nhập OpenAI API Key của bạn để bắt đầu. Key sẽ được lưu trong
            localStorage.
          </p>
          <p className="text-gray-600 mb-4 text-sm">
            Lấy API key tại:{" "}
            <a
              href="https://platform.openai.com/api-keys"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 hover:underline"
            >
              https://platform.openai.com/api-keys
            </a>
          </p>
          <form onSubmit={handleSetApiKey}>
            <input
              type="password"
              placeholder="sk-proj-..."
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded mb-4"
            />
            <button
              type="submit"
              className="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Lưu API Key
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Giao diện chat chính
  return (
    <div className="bg-gray-100 h-screen flex flex-col">
      <div className="container mx-auto p-4 flex flex-col h-full max-w-2xl">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">ChatUI với React + OpenAI</h1>
          <div className="flex gap-2">
            <button
              onClick={handleClearChat}
              className="bg-yellow-500 text-white px-3 py-1 rounded text-sm hover:bg-yellow-600"
            >
              Xóa Chat
            </button>
            <button
              onClick={handleClearKey}
              className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
            >
              Đổi API Key
            </button>
          </div>
        </div>

        <div className="flex-grow overflow-y-auto mb-4 bg-white rounded shadow p-4">
          {chatHistory.length === 0 ? (
            <div className="text-center text-gray-400 mt-10">
              <p>Bắt đầu cuộc trò chuyện bằng cách gửi tin nhắn...</p>
            </div>
          ) : (
            chatHistory.map((chatMessage, i) => (
              <div
                key={i}
                className={`mb-2 ${
                  isBotMessage(chatMessage) ? "text-right" : ""
                }`}
              >
                <p className="text-gray-600 text-sm">
                  {isBotMessage(chatMessage) ? "Bot" : "User"}
                </p>
                <p
                  className={`p-2 rounded-lg inline-block max-w-[80%] whitespace-pre-wrap ${
                    isBotMessage(chatMessage) ? "bg-green-100" : "bg-blue-100"
                  }`}
                >
                  {chatMessage.content}
                </p>
              </div>
            ))
          )}
          <div ref={chatEndRef} />
        </div>

        <form className="flex" onSubmit={submitForm}>
          <input
            type="text"
            placeholder="Tin nhắn của bạn..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="flex-grow p-2 rounded-l border border-gray-300"
          />
          <button
            type="submit"
            disabled={!message.trim()}
            className="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600 disabled:bg-gray-400"
          >
            Gửi tin nhắn
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
