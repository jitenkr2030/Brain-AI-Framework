/**
 * Tests for use-auth hook
 * Brain AI LMS - Frontend Test Suite
 */

import { renderHook, waitFor, act } from '@testing-library/react'
import { useAuth } from '../use-auth'

// Mock window.fetch
global.fetch = jest.fn()
global.localStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
}

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn()
  })
}))

describe('useAuth Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
    // Clear any cached auth state
    ;(global.fetch as jest.Mock).mockReset()
  })

  const mockUser = {
    id: '1',
    email: 'test@example.com',
    username: 'testuser',
    full_name: 'Test User',
    role: 'student',
    is_verified: true
  }

  const mockTokens = {
    access_token: 'test-access-token',
    refresh_token: 'test-refresh-token',
    token_type: 'bearer'
  }

  describe('Initial State', () => {
    it('starts with loading state', async () => {
      ;(global.fetch as jest.Mock).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ ok: true, json: async () => mockUser }), 100))
      )

      const { result } = renderHook(() => useAuth())

      expect(result.current.isLoading).toBe(true)
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.user).toBeNull()
    })

    it('checks for existing session on mount', async () => {
      localStorage.getItem.mockReturnValue('existing-token')

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser
      })

      const { result } = renderHook(() => useAuth())

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/auth/me'),
          expect.objectContaining({
            headers: expect.objectContaining({
              Authorization: 'Bearer existing-token'
            })
          })
        )
      })
    })

    it('sets isAuthenticated to false when no token exists', async () => {
      localStorage.getItem.mockReturnValue(null)

      const { result } = renderHook(() => useAuth())

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
        expect(result.current.isAuthenticated).toBe(false)
      })

      expect(global.fetch).not.toHaveBeenCalled()
    })
  })

  describe('login', () => {
    it('successfully logs in user', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...mockTokens, user: mockUser })
      })

      const { result } = renderHook(() => useAuth())

      await act(async () => {
        const response = await result.current.login({
          email: 'test@example.com',
          password: 'password123'
        })
        expect(response.success).toBe(true)
        expect(response.user).toEqual(mockUser)
      })

      expect(localStorage.setItem).toHaveBeenCalledWith('access_token', 'test-access-token')
      expect(localStorage.setItem).toHaveBeenCalledWith('refresh_token', 'test-refresh-token')
    })

    it('handles login failure', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Invalid credentials' })
      })

      const { result } = renderHook(() => useAuth())

      await act(async () => {
        const response = await result.current.login({
          email: 'test@example.com',
          password: 'wrongpassword'
        })
        expect(response.success).toBe(false)
        expect(response.error).toBe('Invalid credentials')
      })
    })
  })

  describe('register', () => {
    it('successfully registers new user', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ 
          ...mockTokens, 
          user: { ...mockUser, username: 'newuser' }
        })
      })

      const { result } = renderHook(() => useAuth())

      await act(async () => {
        const response = await result.current.register({
          email: 'new@example.com',
          username: 'newuser',
          password: 'password123'
        })
        expect(response.success).toBe(true)
      })
    })

    it('handles registration failure', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Email already registered' })
      })

      const { result } = renderHook(() => useAuth())

      await act(async () => {
        const response = await result.current.register({
          email: 'existing@example.com',
          username: 'existinguser',
          password: 'password123'
        })
        expect(response.success).toBe(false)
        expect(response.error).toBe('Email already registered')
      })
    })
  })

  describe('logout', () => {
    it('clears authentication state', async () => {
      // Set up authenticated state
      localStorage.getItem.mockReturnValue('test-token')
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser
      })

      const { result } = renderHook(() => useAuth())

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      // Logout
      act(() => {
        result.current.logout()
      })

      expect(localStorage.removeItem).toHaveBeenCalledWith('access_token')
      expect(localStorage.removeItem).toHaveBeenCalledWith('refresh_token')
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.user).toBeNull()
    })
  })

  describe('updateProfile', () => {
    it('successfully updates user profile', async () => {
      // Set up authenticated state
      localStorage.getItem.mockReturnValue('test-token')
      ;(global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockUser
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ ...mockUser, full_name: 'Updated Name' })
        })

      const { result } = renderHook(() => useAuth())

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      await act(async () => {
        const response = await result.current.updateProfile({
          full_name: 'Updated Name'
        })
        expect(response.success).toBe(true)
      })

      expect(global.fetch).toHaveBeenCalledTimes(2)
    })

    it('fails when not authenticated', async () => {
      const { result } = renderHook(() => useAuth())

      await act(async () => {
        const response = await result.current.updateProfile({
          full_name: 'New Name'
        })
        expect(response.success).toBe(false)
        expect(response.error).toBe('Not authenticated')
      })
    })
  })
})
