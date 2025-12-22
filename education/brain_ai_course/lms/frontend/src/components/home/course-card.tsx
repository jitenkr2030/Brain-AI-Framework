'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import Image from 'next/image'
import { ClockIcon, StarIcon, UsersIcon } from '@heroicons/react/24/outline'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { formatPrice, getCourseLevelLabel, getCourseLevelColor } from '@/lib/utils'

interface CourseCardProps {
  course: {
    id: string
    title: string
    short_description?: string
    description?: string
    thumbnail_url?: string
    price_usd?: number
    duration_hours?: number
    level?: string
    rating?: number
    students_count?: number
    instructor_name?: string
    has_interactive_labs?: boolean
    has_certification?: boolean
    is_featured?: boolean
  }
  variant?: 'default' | 'compact' | 'featured'
}

export function CourseCard({ course, variant = 'default' }: CourseCardProps) {
  const levelColor = course.level ? getCourseLevelColor(course.level) : ''
  const levelLabel = course.level ? getCourseLevelLabel(course.level) : ''

  if (variant === 'featured') {
    return (
      <motion.div
        whileHover={{ y: -8 }}
        transition={{ duration: 0.2 }}
      >
        <Card className="overflow-hidden group h-full" hoverable>
          {/* Featured Badge */}
          {course.is_featured && (
            <div className="absolute top-4 left-4 z-10">
              <Badge variant="warning" dot>Featured</Badge>
            </div>
          )}
          
          {/* Thumbnail */}
          <div className="relative h-48 bg-gradient-to-br from-indigo-500 to-purple-600">
            {course.thumbnail_url ? (
              <Image
                src={course.thumbnail_url}
                alt={course.title}
                fill
                className="object-cover group-hover:scale-105 transition-transform duration-300"
              />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-6xl font-bold text-white/20">
                  {course.title.charAt(0)}
                </span>
              </div>
            )}
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
            
            {/* Level Badge */}
            <div className="absolute bottom-4 right-4">
              <Badge className={levelColor}>
                {levelLabel}
              </Badge>
            </div>
          </div>

          <div className="p-6">
            {/* Title & Description */}
            <h3 className="text-xl font-bold text-slate-900 mb-2 line-clamp-2">
              {course.title}
            </h3>
            <p className="text-slate-600 mb-4 line-clamp-2">
              {course.short_description || course.description}
            </p>

            {/* Instructor */}
            {course.instructor_name && (
              <div className="flex items-center gap-2 mb-4">
                <div className="w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center">
                  <span className="text-xs font-medium text-indigo-600">
                    {course.instructor_name.charAt(0)}
                  </span>
                </div>
                <span className="text-sm text-slate-500">{course.instructor_name}</span>
              </div>
            )}

            {/* Stats */}
            <div className="flex items-center gap-4 mb-4 text-sm text-slate-500">
              {course.duration_hours && (
                <div className="flex items-center gap-1">
                  <ClockIcon className="w-4 h-4" />
                  <span>{course.duration_hours}h</span>
                </div>
              )}
              {course.rating && (
                <div className="flex items-center gap-1">
                  <StarIcon className="w-4 h-4 text-amber-500 fill-amber-500" />
                  <span>{course.rating.toFixed(1)}</span>
                </div>
              )}
              {course.students_count && (
                <div className="flex items-center gap-1">
                  <UsersIcon className="w-4 h-4" />
                  <span>{course.students_count.toLocaleString()}</span>
                </div>
              )}
            </div>

            {/* Features */}
            <div className="flex flex-wrap gap-2 mb-4">
              {course.has_interactive_labs && (
                <Badge variant="secondary" size="sm">Interactive Labs</Badge>
              )}
              {course.has_certification && (
                <Badge variant="secondary" size="sm">Certification</Badge>
              )}
            </div>

            {/* Price & CTA */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-100">
              <div>
                <span className="text-2xl font-bold text-slate-900">
                  {course.price_usd ? formatPrice(course.price_usd) : 'Free'}
                </span>
              </div>
              <Button asChild>
                <Link href={`/courses/${course.id}`}>View Course</Link>
              </Button>
            </div>
          </div>
        </Card>
      </motion.div>
    )
  }

  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ duration: 0.2 }}
    >
      <Card className="overflow-hidden group" hoverable>
        {/* Thumbnail */}
        <div className="relative h-40 bg-gradient-to-br from-indigo-500 to-purple-600">
          {course.thumbnail_url ? (
            <Image
              src={course.thumbnail_url}
              alt={course.title}
              fill
              className="object-cover group-hover:scale-105 transition-transform duration-300"
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-4xl font-bold text-white/20">
                {course.title.charAt(0)}
              </span>
            </div>
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
          
          {/* Level */}
          <div className="absolute top-3 right-3">
            <Badge className={levelColor}>
              {levelLabel}
            </Badge>
          </div>
        </div>

        <div className="p-4">
          <h3 className="font-semibold text-slate-900 mb-1 line-clamp-1">
            {course.title}
          </h3>
          
          <div className="flex items-center gap-3 text-sm text-slate-500 mb-3">
            {course.duration_hours && (
              <span className="flex items-center gap-1">
                <ClockIcon className="w-4 h-4" />
                {course.duration_hours}h
              </span>
            )}
            {course.rating && (
              <span className="flex items-center gap-1">
                <StarIcon className="w-4 h-4 text-amber-500 fill-amber-500" />
                {course.rating.toFixed(1)}
              </span>
            )}
          </div>

          <div className="flex items-center justify-between">
            <span className="font-bold text-slate-900">
              {course.price_usd ? formatPrice(course.price_usd) : 'Free'}
            </span>
            <Button size="sm" asChild>
              <Link href={`/courses/${course.id}`}>Enroll</Link>
            </Button>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}

interface CourseCardGridProps {
  courses: CourseCardProps['course'][]
  isLoading?: boolean
  variant?: 'default' | 'featured'
}

export function CourseCardGrid({ courses, isLoading, variant = 'default' }: CourseCardGridProps) {
  if (isLoading) {
    return (
      <div className={`grid gap-6 ${variant === 'featured' ? 'md:grid-cols-2 lg:grid-cols-3' : 'md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'}`}>
        {[...Array(6)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="bg-slate-200 rounded-xl h-48 mb-4" />
            <div className="bg-slate-200 h-4 rounded mb-2 w-3/4" />
            <div className="bg-slate-200 h-4 rounded mb-4 w-1/2" />
            <div className="bg-slate-200 h-8 rounded w-1/3" />
          </div>
        ))}
      </div>
    )
  }

  if (!courses.length) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500">No courses found</p>
      </div>
    )
  }

  return (
    <div className={`grid gap-6 ${variant === 'featured' ? 'md:grid-cols-2 lg:grid-cols-3' : 'md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'}`}>
      {courses.map((course) => (
        <CourseCard key={course.id} course={course} variant={variant} />
      ))}
    </div>
  )
}
