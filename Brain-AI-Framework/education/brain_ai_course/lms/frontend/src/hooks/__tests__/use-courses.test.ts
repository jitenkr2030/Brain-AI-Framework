/**
 * Tests for use-courses hook
 * Brain AI LMS - Frontend Test Suite
 */

import { renderHook, waitFor } from '@testing-library/react'
import { useCourses, useCourse, useEnrolledCourses } from '../use-courses'
import * as fetchModule from 'next/dist/server/api-utils/node/fetch'

// Mock environment variables
jest.mock('next/dist/server/api-utils/node/fetch', () => ({
  __esModule: true,
  ...jest.requireActual('next/dist/server/api-utils/node/fetch'),
}))

// Mock window.fetch
global.fetch = jest.fn()

describe('useCourses Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    // Clear environment variable mocks if needed
    delete process.env.NEXT_PUBLIC_API_URL
  })

  const mockCoursesResponse = {
    courses: [
      {
        id: '1',
        title: 'Brain AI Fundamentals',
        slug: 'brain-ai-fundamentals',
        description: 'Foundation course for brain-inspired AI',
        level: 'foundation',
        price_usd: 2500,
        duration_hours: 40,
        is_featured: true
      },
      {
        id: '2',
        title: 'Advanced Memory Systems',
        slug: 'advanced-memory-systems',
        description: 'Advanced course on memory architectures',
        level: 'advanced',
        price_usd: 3500,
        duration_hours: 60,
        is_featured: false
      }
    ],
    total: 2,
    page: 1,
    page_size: 12,
    total_pages: 1
  }

  it('fetches courses on mount', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockCoursesResponse
    })

    const { result } = renderHook(() => useCourses())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    await waitFor(() => {
      expect(result.current.courses).toHaveLength(2)
      expect(result.current.total).toBe(2)
    })
  })

  it('handles fetch errors gracefully', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500
    })

    const { result } = renderHook(() => useCourses())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    await waitFor(() => {
      expect(result.current.error).toBeTruthy()
      expect(result.current.courses).toHaveLength(0)
    })
  })

  it('filters courses by level', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ...mockCoursesResponse,
        courses: [mockCoursesResponse.courses[0]]
      })
    })

    const { result } = renderHook(() => useCourses({ filters: { level: 'foundation' } }))

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('level=foundation'),
      expect.any(Object)
    )
  })

  it('searches courses by keyword', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockCoursesResponse
    })

    const { result } = renderHook(() => useCourses())

    await waitFor(() => {
      result.current.searchCourses({ search: 'brain' })
    })

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('search=brain'),
        expect.any(Object)
      )
    })
  })
})

describe('useCourse Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  const mockCourse = {
    id: '1',
    title: 'Brain AI Fundamentals',
    slug: 'brain-ai-fundamentals',
    description: 'Foundation course for brain-inspired AI',
    level: 'foundation',
    price_usd: 2500,
    duration_hours: 40,
    modules: [
      {
        id: 'm1',
        title: 'Getting Started',
        lessons: [
          { id: 'l1', title: 'Introduction' },
          { id: 'l2', title: 'Setup' }
        ]
      }
    ]
  }

  it('fetches single course by ID', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockCourse
    })

    const { result } = renderHook(() => useCourse('1'))

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    await waitFor(() => {
      expect(result.current.course).toEqual(mockCourse)
      expect(result.current.course?.id).toBe('1')
    })
  })

  it('returns null when courseId is null', async () => {
    const { result } = renderHook(() => useCourse(null))

    await waitFor(() => {
      expect(result.current.course).toBeNull()
      expect(result.current.error).toBeNull()
    })
  })
})

describe('useEnrolledCourses Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
  })

  it('requires authentication', async () => {
    const { result } = renderHook(() => useEnrolledCourses())

    await waitFor(() => {
      expect(result.current.error).toBe('Not authenticated')
    })
  })

  it('fetches enrolled courses when authenticated', async () => {
    localStorage.setItem('token', 'test-token')

    const mockEnrolledCourses = {
      courses: [
        {
          id: '1',
          title: 'Brain AI Fundamentals',
          progress_percentage: 50
        }
      ]
    }

    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockEnrolledCourses
    })

    const { result } = renderHook(() => useEnrolledCourses())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/enrollments/my-courses'),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer test-token'
        })
      })
    )
  })
})
