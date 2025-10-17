import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  SparklesIcon, 
  UserGroupIcon, 
  ChatBubbleLeftRightIcon,
  AcademicCapIcon,
  ClockIcon,
  CheckCircleIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

const LandingPage = () => {
  const features = [
    {
      icon: SparklesIcon,
      title: 'AI-Powered Tutoring',
      description: 'Get instant, intelligent help with Gemini AI for explanations, summaries, and personalized learning.',
      color: 'from-blue-500 to-purple-600'
    },
    {
      icon: UserGroupIcon,
      title: 'Human Expert Tutors',
      description: 'Connect with verified student tutors who have strong academic records in your subjects.',
      color: 'from-purple-500 to-pink-600'
    },
    {
      icon: ChatBubbleLeftRightIcon,
      title: 'Interactive Chat',
      description: 'Real-time conversations with AI and human tutors through our intuitive chat interface.',
      color: 'from-cyan-500 to-blue-600'
    },
    {
      icon: AcademicCapIcon,
      title: 'Personalized Learning',
      description: 'Adaptive learning experience that adjusts to your pace and learning style.',
      color: 'from-indigo-500 to-purple-600'
    },
    {
      icon: ClockIcon,
      title: '24/7 Availability',
      description: 'Access AI tutoring anytime, anywhere. Human tutors available by appointment.',
      color: 'from-emerald-500 to-teal-600'
    },
    {
      icon: CheckCircleIcon,
      title: 'Verified Tutors',
      description: 'All human tutors are verified students with proven academic excellence.',
      color: 'from-orange-500 to-red-600'
    }
  ];

  const benefits = [
    'Instant responses from AI tutor',
    'Connect with top student tutors',
    'Interactive learning experience',
    'Track your learning progress',
    'Affordable tutoring rates',
    'School email verification'
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-32">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50" />
        <div className="absolute inset-0 bg-white/40" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
                Learn Smarter with{' '}
                <span className="gradient-text">
                  AI & Human Tutors
                </span>
              </h1>
              
              <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
                Experience the perfect blend of AI-powered instant help and human expertise. 
                Get personalized tutoring that adapts to your learning style.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12"
            >
              <Link
                to="/register"
                className="btn-primary px-8 py-4 text-lg font-semibold hover-glow flex items-center group"
              >
                Get Started Free
                <ArrowRightIcon className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Link>
              <Link
                to="/login"
                className="px-8 py-4 text-lg font-semibold text-gray-700 hover:text-primary-600 transition-colors"
              >
                Sign In
              </Link>
            </motion.div>

            {/* Hero Visual */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1, delay: 0.4 }}
              className="relative max-w-4xl mx-auto"
            >
              <div className="card p-8 bg-white/60">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  {/* AI Chat Preview */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                      <SparklesIcon className="h-5 w-5 mr-2 text-blue-500" />
                      AI Tutor Chat
                    </h3>
                    <div className="space-y-3">
                      <div className="message-bubble user p-3 rounded-lg text-white text-sm">
                        Can you explain photosynthesis?
                      </div>
                      <div className="message-bubble ai p-3 rounded-lg text-gray-800 text-sm">
                        Photosynthesis is the process by which plants convert light energy into chemical energy...
                      </div>
                    </div>
                  </div>
                  
                  {/* Human Tutor Preview */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                      <UserGroupIcon className="h-5 w-5 mr-2 text-purple-500" />
                      Human Tutors
                    </h3>
                    <div className="space-y-3">
                      {[1, 2].map((i) => (
                        <div key={i} className="flex items-center space-x-3 p-3 bg-white/60 rounded-lg">
                          <div className="w-10 h-10 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full flex items-center justify-center">
                            <span className="text-white font-medium text-sm">T{i}</span>
                          </div>
                          <div className="flex-1 text-left">
                            <div className="text-sm font-medium text-gray-800">Math Tutor</div>
                            <div className="text-xs text-gray-600">GPA 3.9 • $15/hr</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-white/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Why Choose Our Platform?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We combine the best of AI technology and human expertise to create 
              the ultimate learning experience.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="card p-6 hover-glow"
              >
                <div className={`w-12 h-12 bg-gradient-to-r ${feature.color} rounded-xl flex items-center justify-center mb-4`}>
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
                Everything You Need to{' '}
                <span className="gradient-text">Succeed</span>
              </h2>
              <p className="text-xl text-gray-600 mb-8">
                Our platform is designed with students in mind, offering 
                comprehensive features that support your learning journey.
              </p>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {benefits.map((benefit, index) => (
                  <motion.div
                    key={benefit}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    viewport={{ once: true }}
                    className="flex items-center space-x-3"
                  >
                    <CheckCircleIcon className="h-5 w-5 text-green-500 flex-shrink-0" />
                    <span className="text-gray-700">{benefit}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="card p-8 bg-gradient-to-br from-blue-50 to-purple-50">
                <div className="space-y-6">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-gradient-primary rounded-full flex items-center justify-center mx-auto mb-4">
                      <AcademicCapIcon className="h-8 w-8 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      Start Learning Today
                    </h3>
                    <p className="text-gray-600">
                      Join thousands of students already improving their grades
                    </p>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <div className="text-2xl font-bold text-primary-600">1000+</div>
                      <div className="text-sm text-gray-600">Students</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-purple-600">50+</div>
                      <div className="text-sm text-gray-600">Tutors</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-blue-600">24/7</div>
                      <div className="text-sm text-gray-600">AI Support</div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-r from-primary-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
              Ready to Transform Your Learning?
            </h2>
            <p className="text-xl text-blue-100 mb-8">
              Join our community of learners and start your journey with AI and human tutors today.
            </p>
            <Link
              to="/register"
              className="inline-flex items-center px-8 py-4 bg-white text-primary-600 font-semibold rounded-xl hover:bg-gray-50 transition-colors hover-glow group"
            >
              Get Started Now
              <ArrowRightIcon className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;