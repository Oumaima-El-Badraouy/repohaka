import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { CheckCircleIcon } from '@heroicons/react/24/outline';

const PendingStudentsPage = () => {
  const [pendingStudents, setPendingStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPendingStudents();
  }, []);

  const fetchPendingStudents = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/admin/students/pending');
      setPendingStudents(response.data.students);
    } catch (error) {
      toast.error('Failed to fetch pending students');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (studentId) => {
    try {
      await axios.post(`http://localhost:5000/api/admin/students/${studentId}/verify`);
      toast.success('Student verified successfully');
      // Remove the verified student from the list
      setPendingStudents(students => students.filter(s => s._id !== studentId));
    } catch (error) {
      toast.error('Failed to verify student');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Pending Student Verifications</h1>
        <p className="mt-2 text-sm text-gray-600">
          Review and verify student registrations
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center items-center min-h-[60vh]">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      ) : pendingStudents.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-8 text-center">
          <CheckCircleIcon className="mx-auto h-12 w-12 text-green-500" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">All Caught Up!</h3>
          <p className="mt-2 text-sm text-gray-600">
            There are no pending student verifications at this time.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-200">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">School</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Student ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {pendingStudents.map((student) => (
                  <tr key={student._id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{student.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-600">{student.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-600">{student.school}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-600">{student.student_id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => handleVerify(student._id)}
                        className="inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium text-white 
                                 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600
                                 transition-all duration-200 ease-in-out transform hover:scale-105 focus:outline-none 
                                 focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 shadow-sm hover:shadow-md"
                      >
                        <CheckCircleIcon className="h-4 w-4 mr-2" />
                        Verify Student
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default PendingStudentsPage;
