import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuth } from './AuthContext';

const ChatContext = createContext();

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

export const ChatProvider = ({ children }) => {
  const { user, token, isAuthenticated } = useAuth();
  const [chats, setChats] = useState([]);
  const [currentChat, setCurrentChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [loading, setLoading] = useState(false);
  // No real-time socket connection: chat operates over HTTP endpoints only.

  // Load user's chats
  const loadChats = async () => {
    try {
      const response = await axios.get('/ai/chats');
      if (response.data.success) {
        setChats(response.data.chats);
      }
    } catch (error) {
      console.error('Failed to load chats:', error);
      toast.error('Failed to load chat history');
    }
  };

  // Load messages for a specific chat
  const loadMessages = async (chatId) => {
    try {
      setLoading(true);
      const response = await axios.get(`/students/chats?chat_id=${chatId}`);
      if (response.data.success) {
        setMessages(response.data.messages || []);
        setCurrentChat(response.data.chat);
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
      toast.error('Failed to load messages');
    } finally {
      setLoading(false);
    }
  };

  // Create a new chat
  const createChat = async (title = 'New Chat') => {
    try {
      const response = await axios.post('/ai/chats', { title });
      if (response.data.success) {
        const newChat = {
          id: response.data.chat_id,
          title: title,
          created_at: new Date().toISOString(),
          last_activity: new Date().toISOString(),
          message_count: 0,
          total_tokens: 0
        };
        setChats(prev => [newChat, ...prev]);
        return newChat;
      }
    } catch (error) {
      console.error('Failed to create chat:', error);
      toast.error('Failed to create new chat');
      return null;
    }
  };

  // Send message via HTTP (fallback) or WebSocket
  const sendMessage = async (message, chatId = null) => {
    try {
      // If no chatId provided, create a new chat
      let targetChatId = chatId;
      if (!targetChatId) {
        const newChat = await createChat();
        if (!newChat) return false;
        targetChatId = newChat.id;
        setCurrentChat(newChat);
      }

      // Use HTTP API to send message
      {
        // Fallback to HTTP
        const response = await axios.post('/ai/chat', {
          message: message,
          chat_id: targetChatId
        });

        if (response.data.success) {
          // Add messages to state manually since no WebSocket
          const userMessage = {
            sender: 'user',
            text: message,
            timestamp: new Date().toISOString()
          };
          const aiMessage = {
            sender: 'ai',
            text: response.data.message,
            message_id: response.data.message_id,
            timestamp: new Date().toISOString(),
            tutor_suggestions: response.data.tutor_suggestions || []
          };

          setMessages(prev => [...prev, userMessage, aiMessage]);

          // Update chat in list
          setChats(prev => prev.map(chat =>
            chat.id === targetChatId
              ? { ...chat, last_activity: new Date().toISOString(), message_count: chat.message_count + 2 }
              : chat
          ));

          return true;
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      toast.error('Failed to send message');
      return false;
    }
  };

  // Join a chat room (WebSocket)
  const joinChat = (chatId) => {
    // No-op: WebSocket removed
  };

  // Leave a chat room (WebSocket)
  const leaveChat = (chatId) => {
    // No-op: WebSocket removed
  };

  // Start typing indicator
  const startTyping = (chatId) => {
    // No-op: WebSocket removed
  };

  // Stop typing indicator
  const stopTyping = (chatId) => {
    // No-op: WebSocket removed
  };

  // Rate an AI message
  const rateMessage = async (messageId, rating, feedback = null) => {
    try {
      const response = await axios.post('/ai/rate', {
        message_id: messageId,
        rating: rating,
        feedback: feedback
      });

      if (response.data.success) {
        toast.success('Rating submitted successfully');
        return true;
      }
    } catch (error) {
      console.error('Failed to rate message:', error);
      toast.error('Failed to submit rating');
      return false;
    }
  };

  // Delete a chat
  const deleteChat = async (chatId) => {
    try {
      const response = await axios.delete(`/students/chats/${chatId}`);
      if (response.data.success) {
        setChats(prev => prev.filter(chat => chat.id !== chatId));
        if (currentChat?.id === chatId) {
          setCurrentChat(null);
          setMessages([]);
        }
        toast.success('Chat deleted successfully');
        return true;
      }
    } catch (error) {
      console.error('Failed to delete chat:', error);
      toast.error('Failed to delete chat');
      return false;
    }
  };

  // Update chat title
  const updateChatTitle = async (chatId, title) => {
    try {
      const response = await axios.put(`/students/chats/${chatId}/title`, { title });
      if (response.data.success) {
        setChats(prev => prev.map(chat =>
          chat.id === chatId ? { ...chat, title } : chat
        ));
        if (currentChat?.id === chatId) {
          setCurrentChat(prev => ({ ...prev, title }));
        }
        toast.success('Chat title updated');
        return true;
      }
    } catch (error) {
      console.error('Failed to update chat title:', error);
      toast.error('Failed to update title');
      return false;
    }
  };

  const value = {
    // State
    chats,
    currentChat,
    messages,
    isTyping,
    loading,

    // Actions
    loadChats,
    loadMessages,
    createChat,
    sendMessage,
    joinChat,
    leaveChat,
    startTyping,
    stopTyping,
    rateMessage,
    deleteChat,
    updateChatTitle,

    // Setters
    setCurrentChat,
    setMessages
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};