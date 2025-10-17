import React from 'react';
import { motion } from 'framer-motion';
import { ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';

const ChatPage = () => {
  return (
    <div className="min-h-screen pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center py-20"
        >
          <div className="w-24 h-24 bg-gradient-primary rounded-2xl flex items-center justify-center mx-auto mb-6">
            <ChatBubbleLeftRightIcon className="h-12 w-12 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            AI Chat Coming Soon
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Our advanced AI chat interface is currently being finalized. 
            You'll soon be able to have intelligent conversations with our AI tutor!
          </p>
          <div className="space-y-4">
            <div className="card p-6 max-w-md mx-auto">
              <h3 className="font-semibold text-gray-900 mb-2">Features Coming:</h3>
              <ul className="text-left text-gray-600 space-y-2">
                <li>• Real-time AI conversations</li>
                <li>• Code explanations and examples</li>
                <li>• Study help and summaries</li>
                <li>• Interactive quizzes</li>
                <li>• Tutor recommendations</li>
              </ul>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ChatPage;