import React, { useState } from 'react';

function ChatInterface({ apiEndpoint }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      const userMessage = { type: 'user', content: input };
      setMessages([...messages, userMessage]);
      setInput('');

      fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input }),
      })
        .then(response => response.json())
        .then(data => {
          setMessages(prevMessages => [...prevMessages, ...data]);
        })
        .catch(error => {
          console.error('Error:', error);
          setMessages(prevMessages => [...prevMessages, { type: 'assistant', content: 'An error occurred. Please try again.' }]);
        });
    }
  };

  return (
    <div className="chat-interface">
      <div className="message-list">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.type}`}>
            {message.content}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default ChatInterface;