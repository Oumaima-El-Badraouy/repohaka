import React, { useState, Fragment } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Disclosure, Menu, Transition } from '@headlessui/react';
import { Bars3Icon, XMarkIcon, UserIcon, Cog6ToothIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../../contexts/AuthContext';
import { motion } from 'framer-motion';

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const navigation = [
    { name: 'Home', href: '/', current: location.pathname === '/' },
    ...(isAuthenticated() && user?.role === 'student' ? [
      { name: 'Dashboard', href: '/dashboard', current: location.pathname === '/dashboard' },
      { name: 'AI Tutor', href: '/chat', current: location.pathname.startsWith('/chat') },
      { name: 'Human Tutors', href: '/tutors', current: location.pathname === '/tutors' },
    ] : []),
    ...(isAuthenticated() && user?.role === 'admin' ? [
      { name: 'Admin Panel', href: '/admin', current: location.pathname === '/admin' },
      { name: 'Profile', href: '/admin/profile', current: location.pathname === '/admin/profile' }
    ] : []),
  ];

  const userNavigation = [
    { name: 'Profile', href: '/profile', icon: UserIcon },
    { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
  ];

  function classNames(...classes) {
    return classes.filter(Boolean).join(' ');
  }

  return (
    <Disclosure as="nav" className="glass-effect border-b border-white/20 sticky top-0 z-50">
      {({ open }) => (
        <>
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex h-16 items-center justify-between">
              <div className="flex items-center">
                {/* Logo */}
                <Link to="/" className="flex-shrink-0">
                  <motion.div
                    className="flex items-center space-x-2"
                    whileHover={{ scale: 1.05 }}
                    transition={{ duration: 0.2 }}
                  >
                    <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                      <span className="text-white font-bold text-sm">AI</span>
                    </div>
                    <span className="text-xl font-bold gradient-text">
                      Learning Platform
                    </span>
                  </motion.div>
                </Link>

                {/* Desktop Navigation */}
                <div className="hidden md:block ml-10">
                  <div className="flex items-baseline space-x-4">
                    {navigation.map((item) => (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={classNames(
                          item.current
                            ? 'bg-primary-500/10 text-primary-700 border-primary-500/20'
                            : 'text-gray-600 hover:bg-primary-50 hover:text-primary-700',
                          'px-3 py-2 rounded-xl text-sm font-medium transition-all duration-200 border border-transparent'
                        )}
                      >
                        {item.name}
                      </Link>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right side */}
              <div className="hidden md:block">
                <div className="ml-4 flex items-center md:ml-6">
                  {isAuthenticated() ? (
                    /* User menu */
                    <Menu as="div" className="relative ml-3">
                      <div>
                        <Menu.Button className="flex max-w-xs items-center rounded-full bg-white/80 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 p-2 hover:bg-white/90 transition-colors">
                          <span className="sr-only">Open user menu</span>
                          <div className="h-8 w-8 rounded-full bg-gradient-primary flex items-center justify-center">
                            <span className="text-white font-medium text-sm">
                              {user?.name?.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <div className="ml-2 hidden lg:block">
                            <div className="text-sm font-medium text-gray-700">{user?.name}</div>
                            <div className="text-xs text-gray-500 capitalize">{user?.role}</div>
                          </div>
                        </Menu.Button>
                      </div>
                      <Transition
                        as={Fragment}
                        enter="transition ease-out duration-100"
                        enterFrom="transform opacity-0 scale-95"
                        enterTo="transform opacity-100 scale-100"
                        leave="transition ease-in duration-75"
                        leaveFrom="transform opacity-100 scale-100"
                        leaveTo="transform opacity-0 scale-95"
                      >
                        <Menu.Items className="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-xl bg-white/95 backdrop-blur-lg py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                          {userNavigation.map((item) => (
                            <Menu.Item key={item.name}>
                              {({ active }) => (
                                <Link
                                  to={item.href}
                                  className={classNames(
                                    active ? 'bg-gray-50' : '',
                                    'flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50'
                                  )}
                                >
                                  <item.icon className="h-4 w-4 mr-3" />
                                  {item.name}
                                </Link>
                              )}
                            </Menu.Item>
                          ))}
                          <Menu.Item>
                            {({ active }) => (
                              <button
                                onClick={handleLogout}
                                className={classNames(
                                  active ? 'bg-gray-50' : '',
                                  'flex w-full items-center px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50'
                                )}
                              >
                                <ArrowRightOnRectangleIcon className="h-4 w-4 mr-3" />
                                Sign out
                              </button>
                            )}
                          </Menu.Item>
                        </Menu.Items>
                      </Transition>
                    </Menu>
                  ) : (
                    /* Auth buttons */
                    <div className="flex items-center space-x-4">
                      <Link
                        to="/login"
                        className="text-gray-600 hover:text-primary-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                      >
                        Sign in
                      </Link>
                      <Link
                        to="/register"
                        className="btn-primary text-sm px-6 py-2"
                      >
                        Sign up
                      </Link>
                    </div>
                  )}
                </div>
              </div>

              {/* Mobile menu button */}
              <div className="-mr-2 flex md:hidden">
                <Disclosure.Button className="inline-flex items-center justify-center rounded-md bg-white/80 p-2 text-gray-600 hover:bg-white/90 hover:text-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
                  <span className="sr-only">Open main menu</span>
                  {open ? (
                    <XMarkIcon className="block h-6 w-6" aria-hidden="true" />
                  ) : (
                    <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
                  )}
                </Disclosure.Button>
              </div>
            </div>
          </div>

          {/* Mobile menu */}
          <Disclosure.Panel className="md:hidden">
            <div className="space-y-1 px-2 pb-3 pt-2 sm:px-3 bg-white/90 backdrop-blur-lg border-t border-white/20">
              {navigation.map((item) => (
                <Disclosure.Button
                  key={item.name}
                  as={Link}
                  to={item.href}
                  className={classNames(
                    item.current
                      ? 'bg-primary-500/10 text-primary-700'
                      : 'text-gray-600 hover:bg-primary-50 hover:text-primary-700',
                    'block px-3 py-2 rounded-md text-base font-medium'
                  )}
                >
                  {item.name}
                </Disclosure.Button>
              ))}
            </div>
            {isAuthenticated() && (
              <div className="border-t border-gray-200 pb-3 pt-4 bg-white/90">
                <div className="flex items-center px-5">
                  <div className="h-10 w-10 rounded-full bg-gradient-primary flex items-center justify-center">
                    <span className="text-white font-medium">
                      {user?.name?.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div className="ml-3">
                    <div className="text-base font-medium text-gray-800">{user?.name}</div>
                    <div className="text-sm font-medium text-gray-500">{user?.email}</div>
                  </div>
                </div>
                <div className="mt-3 space-y-1 px-2">
                  {userNavigation.map((item) => (
                    <Disclosure.Button
                      key={item.name}
                      as={Link}
                      to={item.href}
                      className="flex items-center px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                    >
                      <item.icon className="h-5 w-5 mr-3" />
                      {item.name}
                    </Disclosure.Button>
                  ))}
                  <Disclosure.Button
                    as="button"
                    onClick={handleLogout}
                    className="flex w-full items-center px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  >
                    <ArrowRightOnRectangleIcon className="h-5 w-5 mr-3" />
                    Sign out
                  </Disclosure.Button>
                </div>
              </div>
            )}
            {!isAuthenticated() && (
              <div className="border-t border-gray-200 pb-3 pt-4 bg-white/90">
                <div className="space-y-1 px-2">
                  <Link
                    to="/login"
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  >
                    Sign in
                  </Link>
                  <Link
                    to="/register"
                    className="block px-3 py-2 rounded-md text-base font-medium bg-gradient-primary text-white hover:opacity-90"
                  >
                    Sign up
                  </Link>
                </div>
              </div>
            )}
          </Disclosure.Panel>
        </>
      )}
    </Disclosure>
  );
};

export default Navbar;