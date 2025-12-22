/**
 * Custom hook for fetching and managing courses data
 * Brain AI LMS - Phase 1: MVP Development
 */

'use client'

import { useState, useEffect, useCallback } from 'react'

export interface Course {
  id: string
  title: string
  slug: string
  description: string
  short_description?: string
  thumbnail_url?: string
  price_usd: number
  level: 'foundation' | 'intermediate' | 'advanced' | 'expert'
  category: string
  duration_hours: number
  difficulty_rating: number
  rating?: number
  students_count?: number
  instructor_name?: string
  has_interactive_labs: boolean
  has_certification: boolean
  has_live_sessions: boolean
  has_community_access: boolean
  is_published: boolean
  is_featured: boolean
  learning_outcomes?: string[]
  prerequisites?: string[]
  created_at?: string
  updated_at?: string
}

export interface CoursesResponse {
  courses: Course[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface CourseFilters {
  search?: string
  level?: string
  category?: string
  min_price?: number
  max_price?: number
  has_labs?: boolean
  has_certification?: boolean
}

interface UseCoursesOptions {
  filters?: CourseFilters
  page?: number
  pageSize?: number
  autoFetch?: boolean
}

export function useCourses(options: UseCoursesOptions = {}) {
  const {
    filters = {},
    page = 1,
    pageSize = 12,
    autoFetch = true
  } = options

  const [courses, setCourses] = useState<Course[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)

  const fetchCourses = useCallback(async (customFilters?: CourseFilters) => {
    setIsLoading(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
      
      const params = new URLSearchParams()
      params.set('page', page.toString())
      params.set('page_size', pageSize.toString())

      const finalFilters = customFilters || filters
      
      if (finalFilters.search) params.set('search', finalFilters.search)
      if (finalFilters.level) params.set('level', finalFilters.level)
      if (finalFilters.category) params.set('category', finalFilters.category)
      if (finalFilters.min_price) params.set('min_price', finalFilters.min_price.toString())
      if (finalFilters.max_price) params.set('max_price', finalFilters.max_price.toString())
      if (finalFilters.has_labs) params.set('has_labs', 'true')
      if (finalFilters.has_certification) params.set('has_certification', 'true')

      const response = await fetch(`${apiUrl}/courses?${params.toString()}`)

      if (!response.ok) {
        throw new Error('Failed to fetch courses')
      }

      const data: CoursesResponse = await response.json()
      setCourses(data.courses)
      setTotal(data.total)
      setTotalPages(data.total_pages)

      return data
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred'
      setError(errorMessage)
      console.error('Error fetching courses:', err)
      return null
    } finally {
      setIsLoading(false)
    }
  }, [page, pageSize, filters])

  useEffect(() => {
    if (autoFetch) {
      fetchCourses()
    }
  }, [autoFetch, fetchCourses])

  const searchCourses = useCallback((searchFilters: CourseFilters) => {
    fetchCourses({ ...filters, ...searchFilters })
  }, [fetchCourses, filters])

  const clearFilters = useCallback(() => {
    fetchCourses({})
  }, [fetchCourses])

  const getFeaturedCourses = useCallback(async () => {
    setIsLoading(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
      const response = await fetch(`${apiUrl}/courses/featured`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch featured courses')
      }

      const data = await response.json()
      return data.courses as Course[]
    } catch (err) {
      console.error('Error fetching featured courses:', err)
      return []
    } finally {
      setIsLoading(false)
    }
  }, [])

  return {
    courses,
    isLoading,
    error,
    total,
    totalPages,
    currentPage: page,
    pageSize,
    fetchCourses,
    searchCourses,
    clearFilters,
    getFeaturedCourses,
    refetch: () => fetchCourses()
  }
}

export function useCourse(courseId: string | null) {
  const [course, setCourse] = useState<Course | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!courseId) {
      setCourse(null)
      return
    }

    const fetchCourse = async () => {
      setIsLoading(true)
      setError(null)

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
        const response = await fetch(`${apiUrl}/courses/${courseId}`)

        if (!response.ok) {
          throw new Error('Failed to fetch course')
        }

        const data = await response.json()
        setCourse(data)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred'
        setError(errorMessage)
        console.error('Error fetching course:', err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchCourse()
  }, [courseId])

  return {
    course,
    isLoading,
    error,
    refetch: () => courseId && setCourse(null) // Trigger re-fetch by resetting
  }
}

export function useEnrolledCourses() {
  const [enrolledCourses, setEnrolledCourses] = useState<Course[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchEnrolledCourses = async () => {
      setIsLoading(true)
      setError(null)

      try {
        const token = localStorage.getItem('token')
        if (!token) {
          setError('Not authenticated')
          return
        }

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
        const response = await fetch(`${apiUrl}/enrollments/my-courses`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (!response.ok) {
          throw new Error('Failed to fetch enrolled courses')
        }

        const data = await response.json()
        setEnrolledCourses(data.courses || [])
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred'
        setError(errorMessage)
        console.error('Error fetching enrolled courses:', err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchEnrolledCourses()
  }, [])

  return {
    enrolledCourses,
    isLoading,
    error,
    refetch: () => setEnrolledCourses([])
  }
}
