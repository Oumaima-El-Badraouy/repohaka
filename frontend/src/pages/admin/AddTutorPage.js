import React, { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const initialState = {
  name: '',
  subjects: '',
  hourly_rate: '',
  school: '',
  gpa: '',
  contact_email: '',
};

const AddTutorPage = () => {
  const [form, setForm] = useState(initialState);
  const [loading, setLoading] = useState(false);

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);

    const data = {
      name: form.name,
      subjects: form.subjects.split(',').map(s => s.trim()).filter(Boolean),
      hourly_rate: form.hourly_rate,
      school: form.school,
      gpa: form.gpa,
      contact_info: { email: form.contact_email },
    };

    try {
      // FIX: Use correct endpoint for proxy setup
      const res = await axios.post('/api/admin/tutors', data);
      if (res.data.success) {
        toast.success('Tutor added successfully!');
        setForm(initialState);
      } else {
        toast.error(res.data.message || 'Failed to add tutor');
      }
    } catch (err) {
      toast.error('Error adding tutor');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-10 bg-white rounded-xl shadow p-8">
      <h2 className="text-2xl font-bold mb-6">Add New Tutor</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Name</label>
          <input name="name" value={form.name} onChange={handleChange} required className="input-primary w-full" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Subjects (comma separated)</label>
          <input name="subjects" value={form.subjects} onChange={handleChange} required className="input-primary w-full" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Hourly Rate</label>
          <input name="hourly_rate" type="number" min="0" step="0.01" value={form.hourly_rate} onChange={handleChange} required className="input-primary w-full" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">School</label>
          <input name="school" value={form.school} onChange={handleChange} required className="input-primary w-full" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">GPA</label>
          <input name="gpa" type="number" min="0" max="4" step="0.01" value={form.gpa} onChange={handleChange} required className="input-primary w-full" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Contact Email</label>
          <input name="contact_email" type="email" value={form.contact_email} onChange={handleChange} required className="input-primary w-full" />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full py-2 mt-4"
        >
          {loading ? 'Adding...' : 'Add Tutor'}
        </button>
      </form>
    </div>
  );
};

export default AddTutorPage;
