import React from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { useChat } from '../../contexts/ChatContext';
import {
  ChatBubbleLeftRightIcon,
  UserGroupIcon,
  ChartBarIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';

const DashboardPage = () => {
  const { user } = useAuth();
  const { chats, loadChats } = useChat();

  React.useEffect(() => {
    loadChats();
  }, []);

  const stats = [
    {
      name: 'AI Conversations',
      value: chats.length,
      icon: ChatBubbleLeftRightIcon,
      color: 'from-blue-500 to-purple-500'
    },
    {
      name: 'Tutors Available',
      value: '50+',
      icon: UserGroupIcon,
      color: 'from-purple-500 to-pink-500'
    },
    {
      name: 'Learning Progress',
      value: '85%',
      icon: ChartBarIcon,
      color: 'from-green-500 to-blue-500'
    },
    {
      name: 'Subjects',
      value: '12',
      icon: AcademicCapIcon,
      color: 'from-orange-500 to-red-500'
    }
  ];

  const quickActions = [
    {
      title: 'Start AI Chat',
      description: 'Get instant help from our AI tutor',
      link: '/chat',
      color: 'from-blue-500 to-purple-500'
    },
    {
      title: 'Find Tutors',
      description: 'Connect with human tutors',
      link: '/tutors',
      color: 'from-purple-500 to-pink-500'
    },
    {
      title: 'View Profile',
      description: 'Manage your learning profile',
      link: '/profile',
      color: 'from-green-500 to-blue-500'
    }
  ];

  return (
    <div className="min-h-screen pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.name}! ὄb
          </h1>
          <p className="text-xl text-gray-600">
            Ready to continue your learning journey?
          </p>
        </motion.div>

        {/* Stats Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          {stats.map((stat, index) => (
            <motion.div
              key={stat.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 * index }}
              className="card p-6 hover-glow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
                <div className={`w-12 h-12 bg-gradient-to-r ${stat.color} rounded-xl flex items-center justify-center`}>
                  <stat.icon className="h-6 w-6 text-white" />
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="mb-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {quickActions.map((action, index) => (
              <motion.div
                key={action.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 * index }}
                className="card p-6 hover-glow"
              >
                <Link to={action.link} className="block">
                  <div className={`w-full h-32 bg-gradient-to-r ${action.color} rounded-xl mb-4 flex items-center justify-center`}>
                    <span className="text-white text-lg font-semibold">{action.title}</span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{action.title}</h3>
                  <p className="text-gray-600">{action.description}</p>
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Recent Chats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Conversations</h2>
          <div className="card p-6">
            {chats.length > 0 ? (
              <div className="space-y-4">
                {chats.slice(0, 5).map((chat) => (
                  <Link
                    key={chat.id}
                    to={`/chat/${chat.id}`}
                    className="flex items-center justify-between p-4 hover:bg-gray-50 rounded-lg transition-colors"
                  >
                    <div>
                      <h3 className="font-medium text-gray-900">{chat.title}</h3>
                      <p className="text-sm text-gray-600">
                        {chat.message_count} messages • {new Date(chat.last_activity).toLocaleDateString()}
                      </p>
                    </div>
                    <ChatBubbleLeftRightIcon className="h-5 w-5 text-gray-400" />
                  </Link>
                ))}
                <Link
                  to="/chat"
                  className="block text-center text-primary-600 hover:text-primary-700 font-medium"
                >
                  View all conversations
                </Link>
              </div>
            ) : (
              <div className="text-center py-8">
                <ChatBubbleLeftRightIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No conversations yet</h3>
                <p className="text-gray-600 mb-4">Start your first chat with our AI tutor!</p>
                <Link to="/chat" className="btn-primary">
                  Start Chatting
                </Link>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default DashboardPage;