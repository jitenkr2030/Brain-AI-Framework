/**
 * WebSocket Hook for Real-time Communication
 * Brain AI LMS - Frontend Integration
 */

'use client'

import { useState, useEffect, useCallback, useRef } from 'react'

interface WebSocketMessage {
  type: string
  data?: any
  content?: string
  username?: string
  user_id?: number
  timestamp?: string
  [key: string]: any
}

interface UseWebSocketOptions {
  url: string
  autoConnect?: boolean
  reconnectAttempts?: number
  reconnectInterval?: number
  onMessage?: (message: WebSocketMessage) => void
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
}

interface UseWebSocketReturn {
  isConnected: boolean
  lastMessage: WebSocketMessage | null
  sendMessage: (message: any) => void
  sendTyping: (isTyping: boolean) => void
  connect: () => void
  disconnect: () => void
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error'
  reconnect: () => void
}

export function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn {
  const {
    url,
    autoConnect = false,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
    onMessage,
    onOpen,
    onClose,
    onError
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectCountRef = useRef(0)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected')
      return
    }

    setConnectionState('connecting')

    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setConnectionState('connected')
        reconnectCountRef.current = 0
        onOpen?.()
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setLastMessage(message)
          onMessage?.(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        setIsConnected(false)
        setConnectionState('disconnected')
        onClose?.()

        // Attempt reconnection if not closed cleanly
        if (event.code !== 1000 && reconnectCountRef.current < reconnectAttempts) {
          reconnectCountRef.current++
          console.log(`Reconnecting... (attempt ${reconnectCountRef.current}/${reconnectAttempts})`)
          setConnectionState('connecting')
          reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnectionState('error')
        onError?.(error)
      }
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      setConnectionState('error')
    }
  }, [url, reconnectAttempts, reconnectInterval, onMessage, onOpen, onClose, onError])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'Client disconnect')
      wsRef.current = null
    }
    
    setIsConnected(false)
    setConnectionState('disconnected')
  }, [])

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected. Cannot send message.')
    }
  }, [])

  const sendTyping = useCallback((isTyping: boolean) => {
    sendMessage({
      type: 'typing',
      is_typing: isTyping
    })
  }, [sendMessage])

  const reconnect = useCallback(() => {
    reconnectCountRef.current = 0
    disconnect()
    setTimeout(connect, 100)
  }, [disconnect, connect])

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [autoConnect, connect, disconnect])

  return {
    isConnected,
    lastMessage,
    sendMessage,
    sendTyping,
    connect,
    disconnect,
    connectionState,
    reconnect
  }
}

// Specialized hook for chat functionality
interface ChatMessage extends WebSocketMessage {
  id: string
  content: string
  username: string
  user_id: number
  timestamp: string
}

interface UseChatOptions extends Omit<UseWebSocketOptions, 'url'> {
  groupId: string
  username: string
  userId: number
}

interface UseChatReturn extends UseWebSocketReturn {
  messages: ChatMessage[]
  sendMessage: (content: string) => void
  sendTyping: (isTyping: boolean) => void
  clearMessages: () => void
  joinGroup: () => void
  leaveGroup: () => void
}

export function useChat(options: UseChatOptions): UseChatReturn {
  const {
    groupId,
    username,
    userId,
    onMessage,
    ...wsOptions
  } = options

  const [messages, setMessages] = useState<ChatMessage[]>([])
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

  const handleMessage = useCallback((message: WebSocketMessage) => {
    onMessage?.(message)
    
    if (message.type === 'message') {
      setMessages(prev => [...prev, message as ChatMessage])
    }
  }, [onMessage])

  const ws = useWebSocket({
    ...wsOptions,
    url: `${apiUrl.replace('/api/v1', '')}/ws/chat/${groupId}`,
    onMessage: handleMessage
  })

  const sendMessageContent = useCallback((content: string) => {
    ws.sendMessage({
      type: 'message',
      content,
      username,
      user_id: userId
    })
  }, [ws, username, userId])

  const joinGroup = useCallback(() => {
    ws.sendMessage({
      type: 'join',
      username,
      user_id: userId
    })
  }, [ws, username, userId])

  const leaveGroup = useCallback(() => {
    ws.sendMessage({
      type: 'leave',
      username,
      user_id: userId
    })
  }, [ws, username, userId])

  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])

  return {
    ...ws,
    messages,
    sendMessage: sendMessageContent,
    sendTyping: ws.sendTyping,
    clearMessages,
    joinGroup,
    leaveGroup
  }
}

// Specialized hook for notifications
interface NotificationData {
  id: string
  type: string
  title: string
  message: string
  data?: any
  timestamp: string
  read: boolean
}

interface UseNotificationsOptions extends Omit<UseWebSocketOptions, 'url'> {
  userId: number
}

interface UseNotificationsReturn extends UseWebSocketReturn {
  notifications: NotificationData[]
  unreadCount: number
  markAsRead: (notificationId: string) => void
  clearAll: () => void
}

export function useNotifications(options: UseNotificationsOptions): UseNotificationsReturn {
  const { userId, onMessage, ...wsOptions } = options
  const [notifications, setNotifications] = useState<NotificationData[]>([])
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

  const handleMessage = useCallback((message: WebSocketMessage) => {
    onMessage?.(message)
    
    if (message.type === 'notification') {
      const notification = message.data as NotificationData
      setNotifications(prev => [notification, ...prev])
    }
  }, [onMessage])

  const ws = useWebSocket({
    ...wsOptions,
    url: `${apiUrl.replace('/api/v1', '')}/ws/notifications`,
    onMessage: handleMessage
  })

  const unreadCount = notifications.filter(n => !n.read).length

  const markAsRead = useCallback((notificationId: string) => {
    setNotifications(prev =>
      prev.map(n =>
        n.id === notificationId ? { ...n, read: true } : n
      )
    )
  }, [])

  const clearAll = useCallback(() => {
    setNotifications([])
  }, [])

  return {
    ...ws,
    notifications,
    unreadCount,
    markAsRead,
    clearAll
  }
}

export default useWebSocket
