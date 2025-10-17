import React, { useEffect, useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';
import { UserIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../../contexts/AuthContext';

const ProfilePage = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [edit, setEdit] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', school: '' });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await axios.get('/students/me'); // <-- removed /api
      if (res.data.success) {
        setProfile(res.data.profile || res.data.user); // support both keys
        setForm({
          name: res.data.profile?.name || res.data.user?.name || '',
          email: res.data.profile?.email || res.data.user?.email || '',
          school: res.data.profile?.school || res.data.user?.school || '',
        });
      }
    } catch (err) {
      toast.error('Failed to load profile');
    }
  };

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSave = async e => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await axios.put('/students/update', form); // <-- removed /api
      if (res.data.success) {
        toast.success('Profile updated!');
        setProfile(res.data.user);
        setEdit(false);
      } else {
        toast.error(res.data.message || 'Update failed');
      }
    } catch (err) {
      toast.error('Update failed');
    } finally {
      setLoading(false);
    }
  };

  if (!profile) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen pt-16 pb-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Profile</h1>
          
          <div className="card p-8">
            <div className="flex items-center space-x-6 mb-8">
              <div className="w-20 h-20 bg-gradient-primary rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-2xl">
                  {user?.name?.charAt(0).toUpperCase()}
                </span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{user?.name}</h2>
                <p className="text-gray-600 capitalize">{user?.role}</p>
                <p className="text-sm text-gray-500">{user?.email}</p>
              </div>
            </div>
            
            {edit ? (
              <form onSubmit={handleSave} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Name</label>
                  <input
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    required
                    className="form-control w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Email</label>
                  <input
                    name="email"
                    type="email"
                    value={form.email}
                    onChange={handleChange}
                    required
                    className="form-control w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">School</label>
                  <input
                    name="school"
                    value={form.school}
                    onChange={handleChange}
                    required
                    className="form-control w-full"
                  />
                </div>
                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={loading}
                    className="btn-primary px-6 py-2"
                  >
                    {loading ? 'Saving...' : 'Save'}
                  </button>
                  <button
                    type="button"
                    className="btn-secondary px-6 py-2"
                    onClick={() => setEdit(false)}
                    disabled={loading}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <div className="space-y-4">
                <div>
                  <span className="font-medium">Name:</span> {profile.name}
                </div>
                <div>
                  <span className="font-medium">Email:</span> {profile.email}
                </div>
                <div>
                  <span className="font-medium">School:</span> {profile.school}
                </div>
                <button
                  className="btn-primary mt-4 px-6 py-2"
                  onClick={() => setEdit(true)}
                >
                  Edit Profile
                </button>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ProfilePage;