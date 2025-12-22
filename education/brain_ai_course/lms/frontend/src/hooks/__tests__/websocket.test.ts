/**
 * Unit Tests for websocket.ts
 * Brain AI LMS - WebSocket Hook Tests
 */

import { renderHook, act, cleanup } from '@testing-library/react';
import { useWebSocket, useChat, useNotifications } from '../websocket';

// Mock WebSocket
class MockWebSocket {
  static instances: MockWebSocket[] = [];
  
  onopen: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  onclose: ((event: { code: number; reason: string }) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  readyState = WebSocket.CONNECTING;
  
  constructor(url: string) {
    MockWebSocket.instances.push(this);
    
    // Simulate connection after a short delay
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      this.onopen?.();
    }, 10);
  }
  
  send(data: string) {
    // Mock send - in real tests, we'd track message sending
  }
  
  close(code: number = 1000, reason?: string) {
    this.readyState = WebSocket.CLOSED;
    this.onclose?.({ code, reason });
  }
}

// Mock window.WebSocket
const originalWebSocket = global.WebSocket;
let mockWebSocketInstance: MockWebSocket | null = null;

beforeEach(() => {
  jest.clearAllMocks();
  MockWebSocket.instances = [];
  
  // Create a mock WebSocket constructor
  mockWebSocketInstance = null;
  (global as any).WebSocket = function(url: string) {
    const instance = new MockWebSocket(url);
    mockWebSocketInstance = instance;
    return instance;
  } as any;
});

afterEach(() => {
  cleanup();
  (global as any).WebSocket = originalWebSocket;
});

describe('useWebSocket', () => {
  it('should initialize with disconnected state', () => {
    const { result } = renderHook(() => useWebSocket({
      url: 'ws://localhost:8080/ws',
      autoConnect: false,
    }));

    expect(result.current.isConnected).toBe(false);
    expect(result.current.connectionState).toBe('disconnected');
    expect(result.current.lastMessage).toBeNull();
  });

  it('should connect when autoConnect is true', async () => {
    const { result } = renderHook(() => useWebSocket({
      url: 'ws://localhost:8080/ws',
      autoConnect: true,
    }));

    expect(result.current.connectionState).toBe('connecting');

    await act(async () => {
      // Wait for WebSocket to connect
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    expect(result.current.isConnected).toBe(true);
    expect(result.current.connectionState).toBe('connected');
  });

  it('should not connect when autoConnect is false', () => {
    const { result } = renderHook(() => useWebSocket({
      url: 'ws://localhost:8080/ws',
      autoConnect: false,
    }));

    expect(result.current.connectionState).toBe('disconnected');
    expect(result.current.isConnected).toBe(false);
  });

  it('should call onOpen callback when connection opens', async () => {
    const onOpen = jest.fn();

    const { result } = renderHook(() => useWebSocket({
      url: 'ws://localhost:8080/ws',
      autoConnect: true,
      onOpen,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    expect(onOpen).toHaveBeenCalled();
  });

  it('should handle incoming messages', async () => {
    const onMessage = jest.fn();
    const testMessage = { type: 'test', data: 'hello' };

    const { result } = renderHook(() => useWebSocket({
      url: 'ws://localhost:8080/ws',
      autoConnect: true,
      onMessage,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({ data: JSON.stringify(testMessage) });
    });

    expect(result.current.lastMessage).toEqual(testMessage);
    expect(onMessage).toHaveBeenCalledWith(testMessage);
  });

  it('should handle message parse error gracefully', async () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation();

    const { result } = renderHook(() => useWebSocket({
      url: 'ws://localhost:8080/ws',
      autoConnect: true,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({ data: 'invalid json' } as any);
    });

    expect(result.current.lastMessage).toBeNull();
    expect(consoleError).toHaveBeenCalled();
    consoleError.mockRestore();
  });

  it('should handle connection close', async () => {
    const onClose = jest.fn();

    const { result } = renderHook(() => useWebSocket({
      url: 'ws://localhost:8080/ws',
      autoConnect: true,
      onClose,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.close(1000, 'Client disconnect');
    });

    expect(result.current.isConnected).toBe(false);
    expect(result.current.connectionState).toBe('disconnected');
    expect(onClose).toHaveBeenCalled();
  });

  it('should attempt reconnection on unexpected close', async () => {
    const { result } = renderHook(() => useWebSocket({
      url: 'ws://localhost:8080/ws',
      autoConnect: true,
      reconnectAttempts: 3,
      reconnectInterval: 100,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    expect(result.current.isConnected).toBe(true);

    // Close with non-clean code
    act(() => {
      mockWebSocketInstance?.close(1001, 'Server error');
    });

    // Should be attempting to reconnect
    expect(result.current.connectionState).toBe('connecting');
  });

  it('should handle connection error', async () => {
    const onError = jest.fn();

    const { result } = renderHook(() => useWebSocket({
      url: 'ws://localhost:8080/ws',
      autoConnect: true,
      onError,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onerror?.({} as Event);
    });

    expect(result.current.connectionState).toBe('error');
    expect(onError).toHaveBeenCalled();
  });

  it('should send message when connected', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useWebSocket({
      url: 'ws://localhost:8080/ws',
      autoConnect: true,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    const testMessage = { type: 'test', content: 'hello' };
    result.current.sendMessage(testMessage);

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify(testMessage));
    sendSpy.mockRestore();
  });

  it('should not send message when not connected', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useWebSocket({
      url: 'ws://localhost:8080/ws',
      autoConnect: false,
    }));

    const testMessage = { type: 'test', content: 'hello' };
    result.current.sendMessage(testMessage);

    expect(sendSpy).not.toHaveBeenCalled();
    sendSpy.mockRestore();
  });

  it('should send typing indicator', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useWebSocket({
      url: 'ws://localhost:8080/ws',
      autoConnect: true,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    result.current.sendTyping(true);
    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'typing',
      is_typing: true,
    }));

    result.current.sendTyping(false);
    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'typing',
      is_typing: false,
    }));
    sendSpy.mockRestore();
  });

  it('should manually reconnect', async () => {
    const { result } = renderHook(() => useWebSocket({
      url: 'ws://localhost:8080/ws',
      autoConnect: true,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      result.current.reconnect();
    });

    // After reconnect, should be in connecting state
    expect(result.current.connectionState).toBe('connecting');
  });

  it('should clean up on unmount', async () => {
    const { unmount } = renderHook(() => useWebSocket({
      url: 'ws://localhost:8080/ws',
      autoConnect: true,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    const closeSpy = jest.spyOn(mockWebSocketInstance!, 'close');
    unmount();

    expect(closeSpy).toHaveBeenCalledWith(1000, 'Client disconnect');
  });
});

describe('useChat', () => {
  const mockChatMessage = {
    id: 'msg-1',
    type: 'message',
    content: 'Hello, world!',
    username: 'testuser',
    user_id: 123,
    timestamp: new Date().toISOString(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should initialize with empty messages', () => {
    const { result } = renderHook(() => useChat({
      groupId: 'group-123',
      username: 'testuser',
      userId: 123,
      autoConnect: false,
    }));

    expect(result.current.messages).toEqual([]);
    expect(result.current.isConnected).toBe(false);
  });

  it('should add received messages to state', async () => {
    const { result } = renderHook(() => useChat({
      groupId: 'group-123',
      username: 'testuser',
      userId: 123,
      autoConnect: true,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({ data: JSON.stringify(mockChatMessage) });
    });

    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0]).toEqual(mockChatMessage);
  });

  it('should send message with correct format', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useChat({
      groupId: 'group-123',
      username: 'testuser',
      userId: 123,
      autoConnect: true,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    result.current.sendMessage('Hello, world!');

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'message',
      content: 'Hello, world!',
      username: 'testuser',
      user_id: 123,
    }));
    sendSpy.mockRestore();
  });

  it('should send join group message', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useChat({
      groupId: 'group-123',
      username: 'testuser',
      userId: 123,
      autoConnect: true,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    result.current.joinGroup();

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'join',
      username: 'testuser',
      user_id: 123,
    }));
    sendSpy.mockRestore();
  });

  it('should send leave group message', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useChat({
      groupId: 'group-123',
      username: 'testuser',
      userId: 123,
      autoConnect: true,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    result.current.leaveGroup();

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'leave',
      username: 'testuser',
      user_id: 123,
    }));
    sendSpy.mockRestore();
  });

  it('should clear all messages', async () => {
    const { result } = renderHook(() => useChat({
      groupId: 'group-123',
      username: 'testuser',
      userId: 123,
      autoConnect: true,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({ data: JSON.stringify(mockChatMessage) });
    });

    expect(result.current.messages.length).toBeGreaterThan(0);

    result.current.clearMessages();
    expect(result.current.messages).toEqual([]);
  });
});

describe('useNotifications', () => {
  const mockNotification = {
    id: 'notif-1',
    type: 'course_update',
    title: 'New Course Available',
    message: 'A new course has been added to your path',
    timestamp: new Date().toISOString(),
    read: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should initialize with empty notifications', () => {
    const { result } = renderHook(() => useNotifications({
      userId: 123,
      autoConnect: false,
    }));

    expect(result.current.notifications).toEqual([]);
    expect(result.current.unreadCount).toBe(0);
  });

  it('should add received notification to state', async () => {
    const { result } = renderHook(() => useNotifications({
      userId: 123,
      autoConnect: true,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({ 
        data: JSON.stringify({ 
          type: 'notification', 
          data: mockNotification 
        }) 
      });
    });

    expect(result.current.notifications).toHaveLength(1);
    expect(result.current.notifications[0]).toEqual(mockNotification);
  });

  it('should calculate unread count correctly', async () => {
    const { result } = renderHook(() => useNotifications({
      userId: 123,
      autoConnect: true,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    const notification1 = { ...mockNotification, id: '1', read: false };
    const notification2 = { ...mockNotification, id: '2', read: true };
    const notification3 = { ...mockNotification, id: '3', read: false };

    act(() => {
      mockWebSocketInstance?.onmessage?.({ 
        data: JSON.stringify({ type: 'notification', data: notification1 }) 
      });
      mockWebSocketInstance?.onmessage?.({ 
        data: JSON.stringify({ type: 'notification', data: notification2 }) 
      });
      mockWebSocketInstance?.onmessage?.({ 
        data: JSON.stringify({ type: 'notification', data: notification3 }) 
      });
    });

    expect(result.current.unreadCount).toBe(2);
  });

  it('should mark notification as read', async () => {
    const { result } = renderHook(() => useNotifications({
      userId: 123,
      autoConnect: true,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({ 
        data: JSON.stringify({ type: 'notification', data: mockNotification }) 
      });
    });

    result.current.markAsRead('notif-1');

    expect(result.current.notifications[0].read).toBe(true);
    expect(result.current.unreadCount).toBe(0);
  });

  it('should clear all notifications', async () => {
    const { result } = renderHook(() => useNotifications({
      userId: 123,
      autoConnect: true,
    }));

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({ 
        data: JSON.stringify({ type: 'notification', data: mockNotification }) 
      });
    });

    expect(result.current.notifications.length).toBeGreaterThan(0);

    result.current.clearAll();
    expect(result.current.notifications).toEqual([]);
    expect(result.current.unreadCount).toBe(0);
  });
});
