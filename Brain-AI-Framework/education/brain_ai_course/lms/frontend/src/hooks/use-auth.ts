/**
 * Custom hook for authentication and user management
 * Brain AI LMS - Phase 1: MVP Development
 */

'use client'

import { useState, useEffect, useCallback } from 'react'

export interface User {
  id: string
  email: string
  username: string
  full_name?: string
  avatar_url?: string
  role: 'student' | 'instructor' | 'admin' | 'enterprise_admin'
  is_verified: boolean
  created_at?: string
  updated_at?: string
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
  full_name?: string
}

export interface AuthTokens {
  access_token: string
  refresh_token?: string
  token_type: string
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true
  })

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token')
      
      if (!token) {
        setState(prev => ({ ...prev, isLoading: false }))
        return
      }

      try {
        const response = await fetch(`${API_URL}/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (response.ok) {
          const userData = await response.json()
          setState({
            user: userData,
            isAuthenticated: true,
            isLoading: false
          })
        } else {
          // Token is invalid or expired
          localStorage.removeItem('token')
          localStorage.removeItem('refresh_token')
          setState({
            user: null,
            isAuthenticated: false,
            isLoading: false
          })
        }
      } catch (error) {
        console.error('Auth check failed:', error)
        setState(prev => ({ ...prev, isLoading: false }))
      }
    }

    checkAuth()
  }, [API_URL])

  const login = useCallback(async (credentials: LoginCredentials) => {
    setState(prev => ({ ...prev, isLoading: true }))

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Login failed')
      }

      const data: AuthTokens & { user: User } = await response.json()

      // Store tokens
      localStorage.setItem('token', data.access_token)
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token)
      }

      setState({
        user: data.user,
        isAuthenticated: true,
        isLoading: false
      })

      return { success: true, user: data.user }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed'
      setState(prev => ({ ...prev, isLoading: false }))
      return { success: false, error: errorMessage }
    }
  }, [API_URL])

  const register = useCallback(async (userData: RegisterData) => {
    setState(prev => ({ ...prev, isLoading: true }))

    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Registration failed')
      }

      const data: AuthTokens & { user: User } = await response.json()

      // Store tokens
      localStorage.setItem('token', data.access_token)
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token)
      }

      setState({
        user: data.user,
        isAuthenticated: true,
        isLoading: false
      })

      return { success: true, user: data.user }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Registration failed'
      setState(prev => ({ ...prev, isLoading: false }))
      return { success: false, error: errorMessage }
    }
  }, [API_URL])

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    setState({
      user: null,
      isAuthenticated: false,
      isLoading: false
    })
  }, [])

  const updateProfile = useCallback(async (profileData: Partial<User>) => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        return { success: false, error: 'Not authenticated' }
      }

      const response = await fetch(`${API_URL}/auth/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(profileData)
      })

      if (!response.ok) {
        throw new Error('Profile update failed')
      }

      const updatedUser = await response.json()
      setState(prev => ({ ...prev, user: updatedUser }))

      return { success: true }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Profile update failed'
      return { success: false, error: errorMessage }
    }
  }, [API_URL])

  const refreshToken = useCallback(async () => {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      return false
    }

    try {
      const response = await fetch(`${API_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refresh_token: refreshToken })
      })

      if (!response.ok) {
        logout()
        return false
      }

      const data: AuthTokens = await response.json()
      localStorage.setItem('token', data.access_token)
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token)
      }

      return true
    } catch (error) {
      logout()
      return false
    }
  }, [API_URL, logout])

  return {
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    login,
    register,
    logout,
    updateProfile,
    refreshToken
  }
}

export function useRequireAuth(redirectTo = '/login') {
  const { isAuthenticated, isLoading } = useAuth()
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        // In a real app, you would use router.push(redirectTo)
        // For now, we'll just set a flag
        console.log('User not authenticated, redirecting to:', redirectTo)
      }
      setIsReady(true)
    }
  }, [isAuthenticated, isLoading, redirectTo])

  return { isReady, isAuthenticated }
}
