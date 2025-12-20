'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  BookOpenIcon, 
  PlayCircleIcon, 
  CodeBracketIcon, 
  AcademicCapIcon,
  StarIcon,
  ClockIcon,
  UsersIcon,
  TrophyIcon,
  SparklesIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { 
  CourseCard, 
  FeaturedCourses, 
  HeroSection, 
  LearningPaths, 
  StatsSection,
  Testimonials,
  PricingSection
} from '@/components/home'
import { useCourses } from '@/hooks/use-courses'
import { useAuth } from '@/hooks/use-auth'

export default function HomePage() {
  const { user } = useAuth()
  const { featuredCourses, courses, isLoading, searchCourses } = useCourses()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedLevel, setSelectedLevel] = useState<string>('')

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    if (query.trim()) {
      searchCourses({ search: query })
    }
  }

  const stats = [
    {
      icon: UsersIcon,
      label: 'Active Learners',
      value: '10,000+',
      description: 'Students worldwide'
    },
    {
      icon: BookOpenIcon,
      label: 'Courses Available',
      value: '25+',
      description: 'Comprehensive curriculum'
    },
    {
      icon: CodeBracketIcon,
      label: 'Interactive Labs',
      value: '100+',
      description: 'Hands-on coding exercises'
    },
    {
      icon: TrophyIcon,
      label: 'Certificates Issued',
      value: '5,000+',
      description: 'Industry-recognized credentials'
    }
  ]

  const features = [
    {
      icon: BrainIcon,
      title: 'Brain-Inspired AI',
      description: 'Learn the cutting-edge approach to artificial intelligence inspired by how the human brain works.',
      color: 'text-purple-600'
    },
    {
      icon: MemoryIcon,
      title: 'Persistent Memory Systems',
      description: 'Master memory architectures that enable AI to learn and remember continuously.',
      color: 'text-blue-600'
    },
    {
      icon: LearningIcon,
      title: 'Incremental Learning',
      description: 'Understand how AI systems can learn from new data without forgetting previous knowledge.',
      color: 'text-green-600'
    },
    {
      icon: CodeIcon,
      title: 'Hands-On Coding',
      description: 'Build real Brain AI applications through interactive labs and practical projects.',
      color: 'text-orange-600'
    }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <HeroSection user={user} />

      {/* Stats Section */}
      <StatsSection stats={stats} />

      {/* Featured Courses */}
      <section className="section">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Featured Courses
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Start your journey with our most popular Brain AI courses designed for different skill levels
            </p>
          </motion.div>

          <FeaturedCourses courses={featuredCourses} isLoading={isLoading} />
        </div>
      </section>

      {/* Learning Features */}
      <section className="section bg-gray-50">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Why Learn with Brain AI LMS?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our platform combines cutting-edge AI education with practical, hands-on learning experiences
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="card-hover text-center h-full">
                  <CardHeader>
                    <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 ${feature.color} mb-4 mx-auto`}>
                      <feature.icon className="w-8 h-8" />
                    </div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600">{feature.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Learning Paths */}
      <LearningPaths />

      {/* Search and Filter */}
      <section className="section">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Explore All Courses
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              Find the perfect course for your skill level and learning goals
            </p>

            {/* Search and Filter */}
            <div className="max-w-4xl mx-auto">
              <div className="flex flex-col md:flex-row gap-4 mb-8">
                <div className="flex-1">
                  <Input
                    type="text"
                    placeholder="Search courses..."
                    value={searchQuery}
                    onChange={(e) => handleSearch(e.target.value)}
                    className="w-full"
                  />
                </div>
                <select
                  value={selectedLevel}
                  onChange={(e) => setSelectedLevel(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">All Levels</option>
                  <option value="foundation">Foundation</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                  <option value="expert">Expert</option>
                </select>
                <Button onClick={() => searchCourses({ search: searchQuery, level: selectedLevel })}>
                  Search
                </Button>
              </div>
            </div>
          </motion.div>

          {/* Course Grid */}
          <CourseCard courses={courses} isLoading={isLoading} />
        </div>
      </section>

      {/* Pricing Section */}
      <PricingSection />

      {/* Testimonials */}
      <Testimonials />

      {/* CTA Section */}
      <section className="section bg-primary-600">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center text-white"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to Master Brain-Inspired AI?
            </h2>
            <p className="text-xl mb-8 max-w-2xl mx-auto opacity-90">
              Join thousands of learners who are already building the future with Brain AI
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" variant="secondary" asChild>
                <Link href="/courses">
                  Start Learning Now
                  <ArrowRightIcon className="ml-2 w-5 h-5" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-primary-600" asChild>
                <Link href="/demo">
                  Try Demo
                  <PlayCircleIcon className="ml-2 w-5 h-5" />
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

// Helper components for icons (since we're using Heroicons)
const BrainIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
  </svg>
)

const MemoryIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
  </svg>
)

const LearningIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
  </svg>
)

const CodeIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
  </svg>
)