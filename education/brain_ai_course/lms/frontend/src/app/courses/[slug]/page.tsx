'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useParams, useRouter } from 'next/navigation'
import Image from 'next/image'
import { motion } from 'framer-motion'
import {
  PlayCircleIcon,
  ClockIcon,
  StarIcon,
  UsersIcon,
  BookOpenIcon,
  CheckIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  ArrowLeftIcon,
  ShareIcon
} from '@heroicons/react/24/outline'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarGroup } from '@/components/ui/avatar'
import { useCourse } from '@/hooks/use-courses'
import { useAuth } from '@/hooks/use-auth'
import { formatPrice, getCourseLevelColor, getCourseLevelLabel } from '@/lib/utils'
import toast from 'react-hot-toast'

interface Module {
  id: string
  title: string
  lessons: Lesson[]
}

interface Lesson {
  id: string
  title: string
  type: 'video' | 'interactive_lab' | 'quiz' | 'assignment' | 'reading'
  duration_minutes: number
  is_free_preview: boolean
}

export default function CourseDetailPage() {
  const params = useParams()
  const router = useRouter()
  const slug = params.slug as string
  const { course, isLoading, error } = useCourse(slug)
  const { isAuthenticated, user } = useAuth()
  const [expandedModules, setExpandedModules] = useState<Set<string>>(new Set())
  const [isEnrolled, setIsEnrolled] = useState(false)

  useEffect(() => {
    // Check if user is enrolled
    if (course && user) {
      // In production, check enrollment status from API
      setIsEnrolled(false) // Placeholder
    }
  }, [course, user])

  const toggleModule = (moduleId: string) => {
    const newExpanded = new Set(expandedModules)
    if (newExpanded.has(moduleId)) {
      newExpanded.delete(moduleId)
    } else {
      newExpanded.add(moduleId)
    }
    setExpandedModules(newExpanded)
  }

  const handleEnroll = () => {
    if (!isAuthenticated) {
      toast.error('Please sign in to enroll')
      router.push('/auth/login')
      return
    }
    router.push(`/checkout/${course?.id}`)
  }

  const handleStartLearning = () => {
    router.push(`/courses/${slug}/learn`)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <div className="animate-pulse">
          <div className="h-80 bg-slate-200" />
          <div className="container mx-auto px-4 py-8">
            <div className="grid lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 space-y-4">
                <div className="h-8 bg-slate-200 rounded w-3/4" />
                <div className="h-4 bg-slate-200 rounded w-full" />
                <div className="h-4 bg-slate-200 rounded w-2/3" />
              </div>
              <div className="h-64 bg-slate-200 rounded-xl" />
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error || !course) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Card className="max-w-md text-center p-8">
          <h2 className="text-2xl font-bold text-slate-900 mb-4">Course Not Found</h2>
          <p className="text-slate-600 mb-6">
            The course you&apos;re looking for doesn&apos;t exist or has been removed.
          </p>
          <Button asChild>
            <Link href="/courses/catalog">Browse All Courses</Link>
          </Button>
        </Card>
      </div>
    )
  }

  const sampleModules: Module[] = [
    {
      id: 'm1',
      title: 'Getting Started',
      lessons: [
        { id: 'l1', title: 'Welcome to the Course', type: 'video', duration_minutes: 5, is_free_preview: true },
        { id: 'l2', title: 'Setting Up Your Environment', type: 'video', duration_minutes: 15, is_free_preview: false },
        { id: 'l3', title: 'Quick Start Guide', type: 'interactive_lab', duration_minutes: 30, is_free_preview: false },
      ]
    },
    {
      id: 'm2',
      title: 'Core Concepts',
      lessons: [
        { id: 'l4', title: 'Understanding Brain-Inspired AI', type: 'video', duration_minutes: 20, is_free_preview: false },
        { id: 'l5', title: 'Memory Architecture Basics', type: 'video', duration_minutes: 25, is_free_preview: false },
        { id: 'l6', title: 'Building Your First Memory System', type: 'interactive_lab', duration_minutes: 45, is_free_preview: false },
        { id: 'l7', title: 'Knowledge Check', type: 'quiz', duration_minutes: 15, is_free_preview: false },
      ]
    },
    {
      id: 'm3',
      title: 'Advanced Topics',
      lessons: [
        { id: 'l8', title: 'Scaling Memory Systems', type: 'video', duration_minutes: 30, is_free_preview: false },
        { id: 'l9', title: 'Performance Optimization', type: 'video', duration_minutes: 25, is_free_preview: false },
        { id: 'l10', title: 'Production Deployment', type: 'interactive_lab', duration_minutes: 60, is_free_preview: false },
      ]
    }
  ]

  const getLessonIcon = (type: string) => {
    switch (type) {
      case 'video': return <PlayCircleIcon className="w-4 h-4" />
      case 'interactive_lab': return <BookOpenIcon className="w-4 h-4" />
      case 'quiz': return <StarIcon className="w-4 h-4" />
      default: return <BookOpenIcon className="w-4 h-4" />
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white">
        <div className="container mx-auto px-4 py-12">
          <Link
            href="/courses/catalog"
            className="inline-flex items-center gap-2 text-slate-300 hover:text-white mb-6 transition-colors"
          >
            <ArrowLeftIcon className="w-4 h-4" />
            Back to Catalog
          </Link>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Course Info */}
            <div className="lg:col-span-2">
              <div className="flex flex-wrap gap-2 mb-4">
                <Badge className={getCourseLevelColor(course.level)}>
                  {getCourseLevelLabel(course.level)}
                </Badge>
                {course.has_interactive_labs && (
                  <Badge variant="secondary">Interactive Labs</Badge>
                )}
                {course.has_certification && (
                  <Badge variant="secondary">Certificate</Badge>
                )}
              </div>

              <h1 className="text-3xl md:text-4xl font-bold mb-4">
                {course.title}
              </h1>

              <p className="text-lg text-slate-300 mb-6">
                {course.short_description || course.description}
              </p>

              {/* Stats */}
              <div className="flex flex-wrap gap-6 mb-6">
                {course.rating && (
                  <div className="flex items-center gap-2">
                    <StarIcon className="w-5 h-5 text-amber-400 fill-amber-400" />
                    <span className="font-medium">{course.rating.toFixed(1)}</span>
                    <span className="text-slate-400">(1,234 reviews)</span>
                  </div>
                )}
                {course.students_count && (
                  <div className="flex items-center gap-2">
                    <UsersIcon className="w-5 h-5" />
                    <span>{course.students_count.toLocaleString()} students</span>
                  </div>
                )}
                {course.duration_hours && (
                  <div className="flex items-center gap-2">
                    <ClockIcon className="w-5 h-5" />
                    <span>{course.duration_hours} hours</span>
                  </div>
                )}
              </div>

              {/* Instructor */}
              {course.instructor_name && (
                <div className="flex items-center gap-3">
                  <Avatar name={course.instructor_name} size="md" />
                  <div>
                    <p className="text-sm text-slate-400">Instructor</p>
                    <p className="font-medium">{course.instructor_name}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Enrollment Card */}
            <div className="lg:col-span-1">
              <Card className="sticky top-6">
                {/* Video Preview */}
                <div className="relative h-48 bg-slate-900 rounded-t-xl overflow-hidden">
                  {course.thumbnail_url ? (
                    <Image
                      src={course.thumbnail_url}
                      alt={course.title}
                      fill
                      className="object-cover"
                    />
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <PlayCircleIcon className="w-16 h-16 text-white/50" />
                    </div>
                  )}
                  <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                    <button className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:bg-white/30 transition-colors">
                      <PlayCircleIcon className="w-12 h-12 text-white" />
                    </button>
                  </div>
                </div>

                <CardContent className="p-6 space-y-4">
                  {/* Price */}
                  <div className="text-center">
                    <span className="text-3xl font-bold text-slate-900">
                      {formatPrice(course.price_usd || 0)}
                    </span>
                    {course.price_usd && course.price_usd > 0 && (
                      <span className="text-sm text-slate-500 ml-2">
                        One-time payment
                      </span>
                    )}
                  </div>

                  {/* CTA Button */}
                  {isEnrolled ? (
                    <Button
                      size="lg"
                      className="w-full"
                      onClick={handleStartLearning}
                    >
                      Continue Learning
                    </Button>
                  ) : (
                    <Button
                      size="lg"
                      className="w-full"
                      onClick={handleEnroll}
                    >
                      Enroll Now
                    </Button>
                  )}

                  {/* Features */}
                  <ul className="space-y-3 pt-4 border-t border-slate-200">
                    {[
                      `${course.duration_hours || 0} hours of content`,
                      course.has_interactive_labs && 'Interactive coding labs',
                      course.has_certification && 'Certificate of completion',
                      'Full lifetime access',
                      'Access on mobile and desktop',
                      '30-day money-back guarantee'
                    ].filter(Boolean).map((feature, index) => (
                      <li key={index} className="flex items-center gap-2 text-sm text-slate-600">
                        <CheckIcon className="w-4 h-4 text-emerald-500 shrink-0" />
                        {feature}
                      </li>
                    ))}
                  </ul>

                  {/* Share */}
                  <div className="flex items-center justify-center gap-4 pt-4 border-t border-slate-200">
                    <button className="flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900">
                      <ShareIcon className="w-4 h-4" />
                      Share
                    </button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>

      {/* Course Content */}
      <div className="container mx-auto px-4 py-12">
        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            {/* Description */}
            <Card>
              <CardHeader>
                <CardTitle>About This Course</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose prose-slate max-w-none">
                  <p>{course.description}</p>
                </div>
              </CardContent>
            </Card>

            {/* Learning Outcomes */}
            {course.learning_outcomes && (
              <Card>
                <CardHeader>
                  <CardTitle>What You&apos;ll Learn</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-3">
                    {course.learning_outcomes.map((outcome, index) => (
                      <div key={index} className="flex items-start gap-2">
                        <CheckIcon className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
                        <span className="text-slate-700">{outcome}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Curriculum */}
            <Card>
              <CardHeader>
                <CardTitle>Course Curriculum</CardTitle>
                <p className="text-sm text-slate-500">
                  {sampleModules.length} modules • {sampleModules.reduce((acc, m) => acc + m.lessons.length, 0)} lessons
                </p>
              </CardHeader>
              <CardContent className="space-y-2">
                {sampleModules.map((module) => {
                  const isExpanded = expandedModules.has(module.id)
                  return (
                    <div key={module.id} className="border border-slate-200 rounded-lg overflow-hidden">
                      <button
                        onClick={() => toggleModule(module.id)}
                        className="w-full flex items-center justify-between p-4 bg-slate-50 hover:bg-slate-100 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          {isExpanded ? (
                            <ChevronUpIcon className="w-5 h-5 text-slate-400" />
                          ) : (
                            <ChevronDownIcon className="w-5 h-5 text-slate-400" />
                          )}
                          <span className="font-medium text-slate-900">
                            {module.title}
                          </span>
                        </div>
                        <span className="text-sm text-slate-500">
                          {module.lessons.length} lessons
                        </span>
                      </button>

                      {isExpanded && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="divide-y divide-slate-200"
                        >
                          {module.lessons.map((lesson) => (
                            <div
                              key={lesson.id}
                              className="flex items-center justify-between p-4 hover:bg-slate-50"
                            >
                              <div className="flex items-center gap-3">
                                {getLessonIcon(lesson.type)}
                                <span className="text-slate-700">{lesson.title}</span>
                                {lesson.is_free_preview && (
                                  <Badge variant="info" size="sm">Preview</Badge>
                                )}
                              </div>
                              <span className="text-sm text-slate-500">
                                {lesson.duration_minutes} min
                              </span>
                            </div>
                          ))}
                        </motion.div>
                      )}
                    </div>
                  )
                })}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Prerequisites */}
            {course.prerequisites && course.prerequisites.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Prerequisites</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {course.prerequisites.map((prereq, index) => (
                      <li key={index} className="flex items-center gap-2 text-sm text-slate-600">
                        <CheckIcon className="w-4 h-4 text-indigo-500" />
                        {prereq}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {/* Similar Courses */}
            <Card>
              <CardHeader>
                <CardTitle>Similar Courses</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Placeholder for similar courses */}
                <div className="text-sm text-slate-500 text-center py-4">
                  Similar course recommendations coming soon
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
