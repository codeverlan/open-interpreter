import React, { useState, useEffect, useRef, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

function ChatInterface({ apiEndpoint, currentProject, selectedFiles, currentAgent }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [taskResult, setTaskResult] = useState(null);
  const messagesEndRef = useRef(null);
  const eventSourceRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const sendMessage = useCallback(async (message, retryCount = 0) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message,
          agentId: currentAgent?.id,
          model: currentAgent?.assigned_model
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      setMessages(prevMessages => [...prevMessages, { type: 'assistant', content: '' }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        lines.forEach(line => {
          if (line.startsWith('data: ')) {
            const token = line.slice(6);
            setMessages(prevMessages => {
              const newMessages = [...prevMessages];
              const lastMessage = newMessages[newMessages.length - 1];
              if (lastMessage.type === 'assistant') {
                lastMessage.content += token;
              } else {
                newMessages.push({ type: 'assistant', content: token });
              }
              return newMessages;
            });
          }
        });
      }

      setIsLoading(false);
    } catch (error) {
      console.error('Error:', error);
      if (retryCount < MAX_RETRIES) {
        setTimeout(() => sendMessage(message, retryCount + 1), RETRY_DELAY);
      } else {
        setError('An error occurred while sending the message. Please try again.');
        setIsLoading(false);
      }
    }
  }, [apiEndpoint, currentAgent]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      const userMessage = { type: 'user', content: input };
      setMessages(prevMessages => [...prevMessages, userMessage]);
      setInput('');
      sendMessage(input);
    }
  };

  const handleCancel = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      setIsLoading(false);
      setError('Message sending was cancelled.');
    }
  };

  const handleTaskSubmit = async (e) => {
    e.preventDefault();
    if (input.trim()) {
      setIsLoading(true);
      setError(null);
      setTaskResult(null);

      try {
        const response = await axios.post('/api/tasks', {
          name: "User Task",
          description: input,
          required_capabilities: [] // You might want to add a way for users to specify required capabilities
        });

        if (response.data.success) {
          setTaskResult(response.data.result);
          setMessages(prevMessages => [
            ...prevMessages,
            { type: 'user', content: input },
            { type: 'assistant', content: `Task result: ${response.data.result}` }
          ]);
        } else {
          setError('Failed to assign task. Please try again.');
        }
      } catch (error) {
        console.error('Error:', error);
        setError('An error occurred while assigning the task. Please try again.');
      } finally {
        setIsLoading(false);
        setInput('');
      }
    }
  };

  return (
    <div className="chat-interface">
      <div className="message-list">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.type}`}>
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        ))}
        {isLoading && <div className="message assistant">Thinking...</div>}
        {error && <div className="message error">{error}</div>}
        {taskResult && <div className="message assistant">Task Result: {taskResult}</div>}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message or task..."
          disabled={isLoading || !currentAgent}
        />
        <button type="submit" disabled={isLoading || !currentAgent}>
          {isLoading ? 'Sending...' : 'Send Message'}
        </button>
        <button type="button" onClick={handleTaskSubmit} disabled={isLoading || !currentAgent}>
          Submit Task
        </button>
        {isLoading && (
          <button type="button" onClick={handleCancel}>
            Cancel
          </button>
        )}
      </form>
      {!currentAgent && (
        <div className="warning">Please select an agent to start chatting or submit tasks.</div>
      )}
      {currentAgent && (
        <div className="agent-info">
          Current Agent: {currentAgent.name} (Model: {currentAgent.assigned_model || 'Not assigned'})
        </div>
      )}
    </div>
  );
}

export default ChatInterface;