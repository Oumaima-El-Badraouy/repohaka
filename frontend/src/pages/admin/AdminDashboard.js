import React from 'react';
import { motion } from 'framer-motion';
import { ChartBarIcon } from '@heroicons/react/24/outline';

const AdminDashboard = () => {
  return (
    <div className="min-h-screen pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center py-20"
        >
          <div className="w-24 h-24 bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <ChartBarIcon className="h-12 w-12 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Admin Dashboard Coming Soon
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            The admin interface for managing users, tutors, and platform analytics 
            is currently under development.
          </p>
          <div className="space-y-4">
            <div className="card p-6 max-w-md mx-auto">
              <h3 className="font-semibold text-gray-900 mb-2">Admin Features:</h3>
              <ul className="text-left text-gray-600 space-y-2">
                <li>• User verification management</li>
                <li>• Tutor approval system</li>
              </ul>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default AdminDashboard;