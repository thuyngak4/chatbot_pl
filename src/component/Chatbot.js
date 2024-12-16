import React, { useState } from 'react';
import axios from 'axios';
import './Chatbot.css';

const Chatbot = () => {
  const [userInput, setUserInput] = useState('');
  const [messages, setMessages] = useState([]);

  // Hàm để gửi câu hỏi và nhận câu trả lời từ backend FastAPI
  const handleSendMessage = async () => {
    if (!userInput.trim()) return;

    // Reset input field ngay lập tức
    const currentInput = userInput; // Lưu tạm giá trị hiện tại của input
    setUserInput('');

    // Cập nhật giao diện người dùng với câu hỏi
    const newMessages = [...messages, { sender: 'user', text: currentInput }];
    setMessages(newMessages);

    // Gửi yêu cầu tới API backend
    try {
      const response = await axios.post('http://127.0.0.1:8000/get_answer/', { query: currentInput });
      const botReply = response.data.answer;

      // Cập nhật giao diện người dùng với câu trả lời
      setMessages([...newMessages, { sender: 'bot', text: botReply }]);
    } catch (error) {
      console.error('Error getting response from server:', error);
      setMessages([...newMessages, { sender: 'bot', text: 'Xin lỗi, tôi không thể trả lời câu hỏi của bạn lúc này.' }]);
    }
  };

  // Hàm xử lý khi nhấn phím Enter
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <h2>Chatbot Tư Vấn Pháp Lý</h2>
      </div>
      <div className="chatbot-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender}`}>
            <p>{message.text}</p>
          </div>
        ))}
      </div>
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
