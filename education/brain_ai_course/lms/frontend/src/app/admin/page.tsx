'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { StatsCard } from '@/components/dashboard/stats-card';

const adminNav = [
  { id: 'overview', label: 'Overview', icon: '📊', href: '/admin' },
  { id: 'users', label: 'Users', icon: '👥', href: '/admin/users' },
  { id: 'courses', label: 'Courses', icon: '📚', href: '/admin/courses' },
  { id: 'content', label: 'Content', icon: '📝', href: '/admin/content' },
  { id: 'analytics', label: 'Analytics', icon: '📈', href: '/admin/analytics' },
  { id: 'settings', label: 'Settings', icon: '⚙️', href: '/admin/settings' },
];

const recentUsers = [
  { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Student', status: 'Active', joined: '2 hours ago' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'Instructor', status: 'Active', joined: '5 hours ago' },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'Student', status: 'Pending', joined: '1 day ago' },
  { id: 4, name: 'Alice Brown', email: 'alice@example.com', role: 'Student', status: 'Active', joined: '2 days ago' },
];

const recentCourses = [
  { id: 1, title: 'Introduction to Python', students: 1250, status: 'Published', revenue: '$12,500' },
  { id: 2, title: 'Advanced JavaScript', students: 890, status: 'Published', revenue: '$8,900' },
  { id: 3, title: 'Machine Learning Basics', students: 2100, status: 'Pending Review', revenue: '$0' },
  { id: 4, title: 'Data Science with R', students: 650, status: 'Draft', revenue: '$0' },
];

export default function AdminDashboardPage() {
  const [activeSection, setActiveSection] = useState('overview');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Admin Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <Badge variant="secondary">LMS Management</Badge>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                Notifications
              </Button>
              <div className="h-8 w-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-medium">
                A
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Admin Sidebar */}
          <Card className="lg:col-span-1 h-fit">
            <CardContent className="pt-6">
              <nav className="space-y-1">
                {adminNav.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => setActiveSection(item.id)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                      activeSection === item.id
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <span className="text-lg">{item.icon}</span>
                    <span className="font-medium">{item.label}</span>
                  </button>
                ))}
              </nav>
            </CardContent>
          </Card>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatsCard
                title="Total Users"
                value="12,847"
                icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>}
                trend={{ value: 12, isPositive: true }}
                color="blue"
              />
              <StatsCard
                title="Active Courses"
                value="342"
                icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>}
                trend={{ value: 8, isPositive: true }}
                color="green"
              />
              <StatsCard
                title="Revenue (MTD)"
                value="$45,230"
                icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
                trend={{ value: 23, isPositive: true }}
                color="purple"
              />
              <StatsCard
                title="Completion Rate"
                value="78.5%"
                icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
                trend={{ value: 5, isPositive: true }}
                color="orange"
              />
            </div>

            {/* Recent Users & Courses */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle>Recent Users</CardTitle>
                  <Button variant="ghost" size="sm" asChild>
                    <Link href="/admin/users">View All</Link>
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {recentUsers.map((user) => (
                      <div key={user.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                        <div className="flex items-center space-x-3">
                          <div className="h-10 w-10 bg-gray-200 rounded-full flex items-center justify-center">
                            <span className="text-sm font-medium text-gray-600">{user.name.charAt(0)}</span>
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">{user.name}</p>
                            <p className="text-sm text-gray-500">{user.email}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge variant={user.status === 'Active' ? 'default' : 'secondary'}>{user.status}</Badge>
                          <p className="text-xs text-gray-500 mt-1">{user.joined}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle>Recent Courses</CardTitle>
                  <Button variant="ghost" size="sm" asChild>
                    <Link href="/admin/courses">View All</Link>
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {recentCourses.map((course) => (
                      <div key={course.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                        <div className="flex-1">
                          <p className="font-medium text-gray-900 line-clamp-1">{course.title}</p>
                          <p className="text-sm text-gray-500">{course.students.toLocaleString()} students</p>
                        </div>
                        <div className="text-right ml-4">
                          <Badge variant={course.status === 'Published' ? 'default' : 'secondary'}>{course.status}</Badge>
                          <p className="text-sm font-medium text-green-600 mt-1">{course.revenue}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Button variant="outline" className="h-20 flex-col" asChild>
                    <Link href="/admin/courses/new">
                      <span className="text-2xl mb-2">📚</span>
                      <span>Add New Course</span>
                    </Link>
                  </Button>
                  <Button variant="outline" className="h-20 flex-col" asChild>
                    <Link href="/admin/users/invite">
                      <span className="text-2xl mb-2">👤</span>
                      <span>Invite Users</span>
                    </Link>
                  </Button>
                  <Button variant="outline" className="h-20 flex-col" asChild>
                    <Link href="/admin/content/create">
                      <span className="text-2xl mb-2">📝</span>
                      <span>Create Content</span>
                    </Link>
                  </Button>
                  <Button variant="outline" className="h-20 flex-col" asChild>
                    <Link href="/admin/analytics/export">
                      <span className="text-2xl mb-2">📊</span>
                      <span>Export Report</span>
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
