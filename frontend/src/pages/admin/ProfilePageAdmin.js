import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';

const ProfilePageAdmin = () => {
  const [user, setUser] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', school: '' });

  useEffect(() => {
    axios.get('/auth/me')
      .then(res => {
        setUser(res.data.user);
        setForm({
          name: res.data.user.name,
          email: res.data.user.email,
          school: res.data.user.school,
        });
      })
      .catch(err => console.error(err));
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleUpdate = async () => {
    try {
      const res = await axios.put('/admin/update', form);
      setUser(res.data.user);
      setIsEditing(false);
      alert('Profile updated successfully!');
    } catch (err) {
      console.error(err);
      alert('Error updating profile.');
    }
  };

  if (!user) return <p>Loading...</p>;

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
              <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-indigo-500 rounded-full flex items-center justify-center text-white font-bold text-2xl">
                {user.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{user.name}</h2>
                <p className="text-gray-600 capitalize">{user.role}</p>
                <p className="text-sm text-gray-500">{user.email}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h3>
                <div className="space-y-3">
                  <p><strong>School:</strong> {user.school}</p>
                  <p><strong>Student ID:</strong> {user.student_id}</p>
                  <p><strong>Status:</strong> {user.is_verified ? 'Verified' : ' Pending ...'}</p>
                </div>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Timestamps</h3>
                <p><strong>Created:</strong> {new Date(user.created_at.$date).toLocaleString()}</p>
                <p><strong>Last login:</strong> {new Date(user.last_login.$date).toLocaleString()}</p>
              </div>
            </div>

            <div className="mt-8 pt-6 border-t border-gray-200">
              <button
                onClick={() => setIsEditing(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg"
              >
                Edit Profile
              </button>
            </div>
          </div>
        </motion.div>

        {/* Modal */}
        {isEditing && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
            <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md">
              <h2 className="text-xl font-semibold mb-4">Edit Profile</h2>
              <div className="space-y-4">
                <input
                  name="name"
                  value={form.name}
                  onChange={handleChange}
                  placeholder="Name"
                  className="border rounded-lg w-full p-2"
                />
                <input
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="Email"
                  className="border rounded-lg w-full p-2"
                />
                <input
                  name="school"
                  value={form.school}
                  onChange={handleChange}
                  placeholder="School"
                  className="border rounded-lg w-full p-2"
                />
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setIsEditing(false)}
                  className="px-4 py-2 bg-gray-300 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpdate}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg"
                >
                  Save
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfilePageAdmin;
