'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

interface Discussion {
  id: string;
  title: string;
  author: {
    name: string;
    avatar: string;
    role: string;
  };
  category: string;
  content: string;
  likes: number;
  replies: number;
  views: number;
  timestamp: string;
  isPinned?: boolean;
}

interface CommunityPageProps {}

const discussions: Discussion[] = [
  {
    id: '1',
    title: 'Best practices for learning Python in 2024?',
    author: { name: 'Sarah Chen', avatar: '', role: 'Student' },
    category: 'General Discussion',
    content: 'I am just starting my Python journey and would love to hear from experienced learners about the best approach...',
    likes: 45,
    replies: 23,
    views: 1250,
    timestamp: '2 hours ago',
    isPinned: true,
  },
  {
    id: '2',
    title: 'Machine Learning Certification - Worth it?',
    author: { name: 'Michael Park', avatar: '', role: 'Student' },
    category: 'Career Advice',
    content: 'Has anyone completed the Machine Learning certification? I am wondering if it is worth the investment...',
    likes: 32,
    replies: 18,
    views: 890,
    timestamp: '5 hours ago',
  },
  {
    id: '3',
    title: 'Help with React Hooks - useEffect dependency array',
    author: { name: 'Emma Wilson', avatar: '', role: 'Instructor' },
    category: 'Technical Help',
    content: 'I am having trouble understanding when to include dependencies in the useEffect hook...',
    likes: 67,
    replies: 34,
    views: 2100,
    timestamp: '1 day ago',
  },
  {
    id: '4',
    title: 'Study group for Data Science bootcamp',
    author: { name: 'Alex Johnson', avatar: '', role: 'Student' },
    category: 'Study Groups',
    content: 'Looking for study partners to join me for the Data Science bootcamp starting next month...',
    likes: 28,
    replies: 45,
    views: 1560,
    timestamp: '2 days ago',
  },
];

const categories = [
  { id: 'all', label: 'All', count: 156 },
  { id: 'general', label: 'General', count: 45 },
  { id: 'technical', label: 'Technical', count: 67 },
  { id: 'career', label: 'Career', count: 23 },
  { id: 'study', label: 'Study Groups', count: 21 },
];

export default function CommunityPage({}: CommunityPageProps) {
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Community</h1>
              <p className="text-gray-600 mt-1">Connect with fellow learners and instructors</p>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" asChild>
                <Link href="/community/create">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  New Discussion
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Search */}
            <Card>
              <CardContent className="pt-6">
                <div className="relative">
                  <Input
                    placeholder="Search discussions..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                  <svg
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
              </CardContent>
            </Card>

            {/* Categories */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Categories</CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-1">
                  {categories.map((category) => (
                    <button
                      key={category.id}
                      onClick={() => setActiveCategory(category.id)}
                      className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition-colors ${
                        activeCategory === category.id
                          ? 'bg-blue-50 text-blue-700'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      <span className="font-medium">{category.label}</span>
                      <Badge variant="secondary">{category.count}</Badge>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Popular Tags */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Popular Tags</CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="flex flex-wrap gap-2">
                  {['Python', 'JavaScript', 'React', 'Machine Learning', 'Data Science', 'Career', 'Study Group'].map((tag) => (
                    <Badge key={tag} variant="outline" className="cursor-pointer hover:bg-gray-100">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Community Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Community Stats</CardTitle>
              </CardHeader>
              <CardContent className="pt-0 space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Members</span>
                  <span className="font-medium">12,847</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Discussions</span>
                  <span className="font-medium">3,429</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Replies</span>
                  <span className="font-medium">28,156</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Online Now</span>
                  <span className="font-medium text-green-600">234</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Featured/Pinned */}
            {discussions.filter(d => d.isPinned).length > 0 && (
              <Card className="border-blue-200 bg-blue-50">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center">
                    <span className="mr-2">📌</span>
                    Pinned Discussion
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  {discussions.filter(d => d.isPinned).map((discussion) => (
                    <DiscussionCard key={discussion.id} discussion={discussion} />
                  ))}
                </CardContent>
              </Card>
            )}

            {/* Recent Discussions */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Recent Discussions</h2>
                <div className="flex items-center space-x-2">
                  <select className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option>Most Recent</option>
                    <option>Most Popular</option>
                    <option>Most Replies</option>
                  </select>
                </div>
              </div>

              {discussions.map((discussion) => (
                <DiscussionCard key={discussion.id} discussion={discussion} />
              ))}

              {/* Load More */}
              <div className="text-center py-8">
                <Button variant="outline">Load More Discussions</Button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function DiscussionCard({ discussion }: { discussion: Discussion }) {
  return (
    <div className="p-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow cursor-pointer">
      <div className="flex items-start space-x-4">
        <div className="h-10 w-10 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
          <span className="text-sm font-medium text-gray-600">{discussion.author.name.charAt(0)}</span>
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-1">
            <Badge variant="outline" className="text-xs">{discussion.category}</Badge>
            {discussion.isPinned && (
              <Badge className="text-xs bg-blue-100 text-blue-700">Pinned</Badge>
            )}
          </div>
          <h3 className="font-semibold text-gray-900 hover:text-blue-600 transition-colors">
            {discussion.title}
          </h3>
          <p className="text-gray-600 text-sm mt-1 line-clamp-2">
            {discussion.content}
          </p>
          <div className="flex items-center space-x-4 mt-3 text-sm text-gray-500">
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              {discussion.likes}
            </span>
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              {discussion.replies}
            </span>
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              {discussion.views}
            </span>
            <span>{discussion.timestamp}</span>
            <span className="text-gray-400">by</span>
            <span className="font-medium text-gray-700">{discussion.author.name}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
