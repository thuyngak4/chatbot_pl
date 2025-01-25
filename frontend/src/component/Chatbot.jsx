import { useState,useEffect, useRef  } from 'react';
import axios from 'axios';
import './Chatbot.css';
import robotIcon from '../assets/robot_icon.png';
import userIcon from '../assets/user.png';
const Chatbot = () => {
  const [userInput, setUserInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  // Hàm để gửi câu hỏi và nhận câu trả lời từ backend FastAPI
  const handleSendMessage = async () => {
    if (!userInput.trim()) return;

    // Reset input field ngay lập tức
    const currentInput = userInput; // Lưu tạm giá trị hiện tại của input
    setUserInput('');

    // Cập nhật giao diện người dùng với câu hỏi
    const newMessages = [...messages, { sender: 'user', text: currentInput }];
    setMessages(newMessages);

    setIsTyping(true);
    // Gửi yêu cầu tới API backend
    try {
      const response = await axios.post('http://127.0.0.1:8000/get_answer/', { query: currentInput },"streamer");
      let botReply = response.data.results;
      // botReply = botReply.replace(/\s+/g, ' ').trim(); // Xóa khoảng trắng thừa
      botReply = botReply.replace(/(\d+\.\s)/g, '\n$1') // Thêm xuống dòng trước các số thứ tự (1. , 2. , ...)
      botReply = botReply.replace(/([a-zA-Z]\)\s)/g, '\n$1');
      botReply = botReply.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');


      botReply = botReply.replace(/-\s/g, '\n- '); // Thêm xuống dòng trước dấu gạch đầu dòng
      // Cập nhật giao diện người dùng với câu trả lời
      setMessages([...newMessages, { sender: 'bot', text: botReply }]);
    } catch (error) {
      console.error('Error getting response from server:', error);
      setMessages([...newMessages, { sender: 'bot', text: 'Xin lỗi, tôi không thể trả lời câu hỏi của bạn lúc này.' }]);
    } finally {
      setIsTyping(false);
    }
  };

  // Hàm xử lý khi nhấn phím Enter
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <h2>CHATBOT TƯ VẤN LUẬT HÔN NHÂN VÀ GIA ĐÌNH</h2>
      </div>
      <div className="chatbot-messages">
  {messages.map((message, index) => (
    <div key={index} className={`message-container ${message.sender}`}>
      {/* Hiển thị icon */}
      {message.sender === 'bot' ? (
        <img
          src={robotIcon}
          alt="Bot Icon"
          className="message-icon"
        />
      ) : (
        <img
          src={userIcon}
          alt="User Icon"
          className="message-icon"
        />
      )}

      {/* Hiển thị nội dung tin nhắn */}
      <div className={`message ${message.sender}`}>
        {message.sender === 'bot' ? (
          // Xử lý tin nhắn bot: định dạng **in đậm** và xuống dòng
          <div
            dangerouslySetInnerHTML={{
              __html: message.text
                .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>') // In đậm với **text**
                .replace(/\n/g, '<br />'), // Thay ký tự xuống dòng bằng <br />
            }}
          />
        ) : (
          // Hiển thị tin nhắn của người dùng
          <pre>{message.text}</pre>
        )}
      </div>
    </div>
  ))}
  <div ref={messagesEndRef} /> {/* Vị trí cuối cùng để cuộn đến */}    
</div>


      {/* Typing indicator */}
      {isTyping && (
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}
      <div className="chatbot-input">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyDown={handleKeyDown} // Thêm sự kiện lắng nghe phím Enter
          placeholder="Hãy nhập câu hỏi của bạn..."
        />
        <button onClick={handleSendMessage}>Gửi</button>
      </div>
    </div>
  );
};

export default Chatbot;
