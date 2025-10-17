import React from 'react';
import { motion } from 'framer-motion';
import { UserGroupIcon } from '@heroicons/react/24/outline';

const TutorsPage = () => {
  return (
    <div className="min-h-screen pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center py-20"
        >
          <div className="w-24 h-24 bg-gradient-secondary rounded-2xl flex items-center justify-center mx-auto mb-6">
            <UserGroupIcon className="h-12 w-12 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Human Tutors Coming Soon
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            We're building a comprehensive platform to connect you with verified student tutors. 
            Browse profiles, check ratings, and book sessions easily!
          </p>
          <div className="space-y-4">
            <div className="card p-6 max-w-md mx-auto">
              <h3 className="font-semibold text-gray-900 mb-2">What to Expect:</h3>
              <ul className="text-left text-gray-600 space-y-2">
                <li>• Verified student tutors</li>
                <li>• GPA and rating system</li>
                <li>• Subject-specific expertise</li>
                <li>• Flexible scheduling</li>
                <li>• Transparent pricing</li>
              </ul>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default TutorsPage;