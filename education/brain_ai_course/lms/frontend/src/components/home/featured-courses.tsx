'use client'

import { motion } from 'framer-motion'
import { CourseCard, CourseCardGrid } from './course-card'

interface FeaturedCoursesProps {
  courses?: {
    id: string
    title: string
    short_description?: string
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
  }[]
  isLoading?: boolean
}

export function FeaturedCourses({ courses = [], isLoading }: FeaturedCoursesProps) {
  const featured = courses.filter(c => c.is_featured).length > 0 
    ? courses.filter(c => c.is_featured) 
    : courses.slice(0, 6)

  return (
    <div className="space-y-8">
      {isLoading ? (
        <CourseCardGrid courses={[]} isLoading isLoading />
      ) : (
        <CourseCardGrid courses={featured} variant="featured" />
      )}
      
      {/* View All Link */}
      <div className="text-center">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          <a
            href="/courses"
            className="inline-flex items-center gap-2 text-indigo-600 font-medium hover:text-indigo-700 transition-colors"
          >
            View All Courses
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 8l4 4m0 0l-4 4m4-4H3"
              />
            </svg>
          </a>
        </motion.div>
      </div>
    </div>
  )
}
