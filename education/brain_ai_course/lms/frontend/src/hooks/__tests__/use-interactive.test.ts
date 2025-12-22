/**
 * Unit Tests for use-interactive.ts
 * Brain AI LMS - Interactive Learning Hook Tests
 */

import { renderHook, waitFor, act } from '@testing-library/react';
import { useWebSocket, useCodeExecution, useAITutor, usePeerReview, useMentorship, useCollaboration } from '../use-interactive';

// Mock toast
jest.mock('react-hot-toast', () => ({
  toast: {
    error: jest.fn(),
    success: jest.fn(),
  },
}));

// Mock useAuth hook
jest.mock('./use-auth', () => ({
  useAuth: () => ({
    user: { token: 'mock-token', id: 123 },
  }),
}));

// Mock WebSocket
class MockWebSocket {
  onopen: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  readyState = WebSocket.CONNECTING;
  
  constructor(url: string) {
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      this.onopen?.();
    }, 10);
  }
  
  send(data: string) {}
  
  close() {
    this.readyState = WebSocket.CLOSED;
    this.onclose?.();
  }
}

const originalWebSocket = global.WebSocket;
let mockWebSocketInstance: MockWebSocket | null = null;

beforeEach(() => {
  jest.clearAllMocks();
  
  // Create a mock WebSocket constructor
  mockWebSocketInstance = null;
  (global as any).WebSocket = function(url: string) {
    const instance = new MockWebSocket(url);
    mockWebSocketInstance = instance;
    return instance;
  } as any;
});

afterEach(() => {
  (global as any).WebSocket = originalWebSocket;
});

describe('useWebSocket', () => {
  it('should initialize with disconnected state', () => {
    const { result } = renderHook(() => useWebSocket());

    expect(result.current.isConnected).toBe(false);
    expect(result.current.socket).toBeNull();
    expect(result.current.connectionId).toBeNull();
  });

  it('should connect when user token is available', async () => {
    const { result } = renderHook(() => useWebSocket());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    expect(result.current.isConnected).toBe(true);
    expect(result.current.socket).not.toBeNull();
  });

  it('should not connect without user token', () => {
    jest.resetModules();
    jest.doMock('./use-auth', () => ({
      useAuth: () => ({ user: null }),
    }));

    // Re-import to get fresh module
    const { useWebSocket: useWebSocketFresh } = require('../use-interactive');
    const { result } = renderHook(() => useWebSocketFresh());

    expect(result.current.isConnected).toBe(false);
  });

  it('should send messages when connected', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useWebSocket());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    const testMessage = { type: 'test', content: 'hello' };
    result.current.sendMessage(testMessage);

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify(testMessage));
    sendSpy.mockRestore();
  });

  it('should handle reconnection on close', async () => {
    const { result } = renderHook(() => useWebSocket());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    expect(result.current.isConnected).toBe(true);

    act(() => {
      mockWebSocketInstance?.close();
    });

    // Should attempt reconnection after delay
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 3100));
    });

    expect(result.current.isConnected).toBe(true);
  });

  it('should clean up on unmount', async () => {
    const closeSpy = jest.spyOn(MockWebSocket.prototype, 'close');

    const { unmount } = renderHook(() => useWebSocket());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    unmount();

    expect(closeSpy).toHaveBeenCalled();
    closeSpy.mockRestore();
  });
});

describe('useCodeExecution', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should initialize with empty state', () => {
    const { result } = renderHook(() => useCodeExecution());

    expect(result.current.isExecuting).toBe(false);
    expect(result.current.executionHistory).toEqual([]);
    expect(result.current.currentExecution).toBeNull();
  });

  it('should not execute when not connected', () => {
    const toast = require('react-hot-toast').toast;

    const { result } = renderHook(() => useCodeExecution());

    result.current.executeCode({
      code: 'print("hello")',
      language: 'python',
    });

    expect(toast.error).toHaveBeenCalledWith('Not connected to execution server');
  });

  it('should handle execution start message', async () => {
    const { result } = renderHook(() => useCodeExecution());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'code_execution_start',
          execution_id: 'exec-123',
        }),
      });
    });

    expect(result.current.currentExecution).not.toBeNull();
    expect(result.current.currentExecution?.executionId).toBe('exec-123');
    expect(result.current.currentExecution?.status).toBe('pending');
  });

  it('should handle execution output message', async () => {
    const { result } = renderHook(() => useCodeExecution());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'code_execution_start',
          execution_id: 'exec-123',
        }),
      });
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'execution_output',
          output: 'Hello, World!',
        }),
      });
    });

    expect(result.current.currentExecution?.output).toContain('Hello, World!');
  });

  it('should handle execution complete message', async () => {
    const toast = require('react-hot-toast').toast;

    const { result } = renderHook(() => useCodeExecution());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'code_execution_start',
          execution_id: 'exec-123',
        }),
      });
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'execution_complete',
          execution_id: 'exec-123',
          status: 'success',
          output: 'Hello, World!',
          execution_time: 150,
          stdout: 'Hello, World!\n',
          stderr: '',
        }),
      });
    });

    expect(result.current.currentExecution?.status).toBe('success');
    expect(result.current.executionHistory.length).toBe(1);
    expect(toast.success).toHaveBeenCalledWith('Code executed successfully!');
  });

  it('should handle execution error', async () => {
    const toast = require('react-hot-toast').toast;

    const { result } = renderHook(() => useCodeExecution());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'execution_complete',
          execution_id: 'exec-123',
          status: 'error',
          error: 'SyntaxError: invalid syntax',
        }),
      });
    });

    expect(result.current.currentExecution?.status).toBe('error');
    expect(result.current.currentExecution?.error).toBe('SyntaxError: invalid syntax');
    expect(toast.error).toHaveBeenCalledWith('Execution failed: SyntaxError: invalid syntax');
  });

  it('should handle execution error message type', async () => {
    const toast = require('react-hot-toast').toast;

    const { result } = renderHook(() => useCodeExecution());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'execution_error',
          error: 'Runtime error: division by zero',
        }),
      });
    });

    expect(result.current.isExecuting).toBe(false);
    expect(toast.error).toHaveBeenCalledWith('Execution error: Runtime error: division by zero');
  });

  it('should add completed execution to history', async () => {
    const { result } = renderHook(() => useCodeExecution());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    // First execution
    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'execution_complete',
          execution_id: 'exec status: 'success-1',
         ',
          output:',
          'Output 1      });
    });

    // Second execution
    act(() => {
      mockWebSocketInstance?. execution_time: onmessage?.({
100,
        }),
        data: JSON: 'execution_complete',
          execution_id: 'exec-.stringify({
          type2',
          status: 'success',
          output: 'Output 2',
          execution_time: 120,
        }),
      });
    });

    expect(result.current.extoBe(2ecutionHistory.length)..current.executionHistory);
    expect(result[0].executionId).toBe('exec-2.current.executionHistory');
    expect(result[1].executionId).toBe('exec-1');
  });
});

describe('useAITutor', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should initialize with empty messages', () => {
    const { result } = renderHook(() => useAITutor());

    expect(result.current.messages).toEqual([]);
    expect(result.current.isTyping).toBe(false);
    expect(result.current.conversationId).toBeNull();
  });

  it('should send message to tutor', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useAITutor());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    result.current.sendMessageToTutor('What is a neural network?');

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'ai_tutor_chat',
      data: expect.objectContaining({
        question: 'What is a neural network?',
        conversation_id: null,
      }),
    }));
    sendSpy.mockRestore();
  });

  it('should add user message to state', async () => {
    const { result } = renderHook(() => useAITutor());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      result.current.sendMessageToTutor('Test question');
    });

    expect(result.current.messages.length).toBe(1);
    expect(result.current.messages[0].content).toBe('Test question');
    expect(result.current.messages[0].type).toBe('user');
    expect(result.current.isTyping).toBe(true);
  });

  it('should not send empty messages', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useAITutor());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    result.current.sendMessageToTutor('   ');

    expect(sendSpy).not.toHaveBeenCalled();
    expect(result.current.messages).toEqual([]);
    sendSpy.mockRestore();
  });

  it('should handle tutor response', async () => {
    const { result } = renderHook(() => useAITutor());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      result.current.sendMessageToTutor('What is AI?');
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'ai_tutor_response',
          data: {
            query_id: 'query-123',
            response: 'AI is artificial intelligence...',
            code_example: 'def ai(): pass',
            resources: ['Resource 1', 'Resource 2'],
            timestamp: '2024-02-01T10:00:00Z',
          },
        }),
      });
    });

    expect(result.current.messages.length).toBe(2);
    expect(result.current.messages[1].content).toBe('AI is artificial intelligence...');
    expect(result.current.messages[1].type).toBe('assistant');
    expect(result.current.conversationId).toBe('query-123');
    expect(result.current.isTyping).toBe(false);
  });

  it('should clear conversation', async () => {
    const { result } = renderHook(() => useAITutor());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      result.current.sendMessageToTutor('Question 1');
    });

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'ai_tutor_response',
          data: { query_id: 'q1', response: 'Answer 1' },
        }),
      });
    });

    expect(result.current.messages.length).toBe(2);

    result.current.clearConversation();

    expect(result.current.messages).toEqual([]);
    expect(result.current.conversationId).toBeNull();
  });

  it('should use existing conversation ID for follow-up questions', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useAITutor());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    // First message
    act(() => {
      result.current.sendMessageToTutor('What is AI?');
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'ai_tutor_response',
          data: { query_id: 'conv-123', response: 'AI is...' },
        }),
      });
    });

    // Second message (follow-up)
    result.current.sendMessageToTutor('Tell me more');

    expect(sendSpy).toHaveBeenLastCalledWith(JSON.stringify({
      type: 'ai_tutor_chat',
      data: expect.objectContaining({
        question: 'Tell me more',
        conversation_id: 'conv-123',
      }),
    }));
    sendSpy.mockRestore();
  });
});

describe('usePeerReview', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should initialize with empty state', () => {
    const { result } = renderHook(() => usePeerReview());

    expect(result.current.submissions).toEqual([]);
    expect(result.current.pendingReviews).toEqual([]);
    expect(result.current.isLoading).toBe(false);
  });

  it('should submit code for review', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');
    const toast = require('react-hot-toast').toast;

    const { result } = renderHook(() => usePeerReview());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    result.current.submitForReview({
      lessonId: 101,
      title: 'Binary Search Implementation',
      description: 'My binary search solution',
      code: 'def binary_search(arr, target): ...',
      language: 'python',
    });

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'peer_review',
      data: expect.objectContaining({
        action: 'submit_code',
        lessonId: 101,
        title: 'Binary Search Implementation',
      }),
    }));
    sendSpy.mockRestore();
  });

  it('should handle submission confirmation', async () => {
    const toast = require('react-hot-toast').toast;

    const { result } = renderHook(() => usePeerReview());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'peer_review_submitted',
          data: {
            success: true,
            submission_id: 'sub-123',
            title: 'Binary Search',
            description: 'My solution',
            code: '...',
            language: 'python',
          },
        }),
      });
    });

    expect(result.current.submissions.length).toBe(1);
    expect(result.current.submissions[0].submissionId).toBe('sub-123');
    expect(toast.success).toHaveBeenCalledWith('Code submitted for review successfully!');
  });

  it('should handle submission error', async () => {
    const toast = require('react-hot-toast').toast;

    const { result } = renderHook(() => usePeerReview());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'peer_review_submitted',
          data: {
            success: false,
            error: 'Submission limit reached',
          },
        }),
      });
    });

    expect(toast.error).toHaveBeenCalledWith('Submission limit reached');
  });

  it('should submit feedback', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => usePeerReview());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    result.current.submitFeedback('review-123', {
      overallScore: 8,
      detailedFeedback: { clarity: 8, efficiency: 7, style: 9 },
      strengths: ['Clean code'],
      improvements: ['Add comments'],
    });

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'peer_review',
      data: expect.objectContaining({
        action: 'submit_feedback',
        review_request_id: 'review-123',
      }),
    }));
    sendSpy.mockRestore();
  });

  it('should handle feedback submission confirmation', async () => {
    const toast = require('react-hot-toast').toast;

    const { result } = renderHook(() => usePeerReview());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'peer_review_feedback_submitted',
          data: {
            success: true,
          },
        }),
      });
    });

    expect(toast.success).toHaveBeenCalledWith('Feedback submitted successfully!');
  });

  it('should get submission reviews', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => usePeerReview());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    result.current.getSubmissionReviews('sub-123');

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'peer_review',
      data: expect.objectContaining({
        action: 'get_reviews',
        submission_id: 'sub-123',
      }),
    }));
    sendSpy.mockRestore();
  });

  it('should get reviewer dashboard', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => usePeerReview());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    result.current.getReviewerDashboard();

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'peer_review',
      data: expect.objectContaining({
        action: 'get_dashboard',
      }),
    }));
    sendSpy.mockRestore();
  });
});

describe('useMentorship', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should initialize with empty state', () => {
    const { result } = renderHook(() => useMentorship());

    expect(result.current.mentors).toEqual([]);
    expect(result.current.mentorshipSessions).toEqual([]);
    expect(result.current.isLoading).toBe(false);
  });

  it('should find mentors', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useMentorship());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    result.current.findMentors({
      expertiseAreas: ['Machine Learning', 'NLP'],
      sessionType: 'video',
      budget: 50,
    });

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'mentorship',
      data: expect.objectContaining({
        action: 'find_mentors',
        expertiseAreas: ['Machine Learning', 'NLP'],
      }),
    }));
    sendSpy.mockRestore();
  });

  it('should handle mentor search results', async () => {
    const mockMentors = [
      { id: 1, name: 'Dr. Smith', expertise: ['ML', 'NLP'], rating: 4.8 },
      { id: 2, name: 'Prof. Johnson', expertise: ['Deep Learning'], rating: 4.9 },
    ];

    const { result } = renderHook(() => useMentorship());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'mentor_search_results',
          data: {
            success: true,
            mentors: mockMentors,
          },
        }),
      });
    });

    expect(result.current.mentors).toEqual(mockMentors);
  });

  it('should request mentorship session', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useMentorship());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    result.current.requestMentorship({
      expertiseAreas: ['Data Science'],
      goals: ['Learn data analysis'],
      sessionType: 'video',
      durationMinutes: 60,
    });

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'mentorship',
      data: expect.objectContaining({
        action: 'request_session',
        expertiseAreas: ['Data Science'],
      }),
    }));
    sendSpy.mockRestore();
  });

  it('should handle mentorship request confirmation', async () => {
    const toast = require('react-hot-toast').toast;

    const { result } = renderHook(() => useMentorship());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'mentorship_requested',
          data: {
            success: true,
            sessionId: 'session-123',
          },
        }),
      });
    });

    expect(toast.success).toHaveBeenCalledWith('Mentorship request submitted successfully!');
  });

  it('should get dashboard', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useMentorship());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    result.current.getDashboard('mentee');

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'mentorship',
      data: expect.objectContaining({
        action: 'get_dashboard',
        dashboard_type: 'mentee',
      }),
    }));
    sendSpy.mockRestore();
  });

  it('should handle dashboard data', async () => {
    const mockDashboard = {
      success: true,
      upcoming_sessions: [
        { id: 's1', mentor: 'Dr. Smith', time: '2024-02-05T14:00:00Z' },
      ],
      past_sessions: [],
    };

    const { result } = renderHook(() => useMentorship());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'mentorship_dashboard',
          data: mockDashboard,
        }),
      });
    });

    expect(result.current.dashboardData).toEqual(mockDashboard);
    expect(result.current.mentorshipSessions.length).toBe(1);
  });
});

describe('useCollaboration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should initialize with empty state', () => {
    const { result } = renderHook(() => useCollaboration());

    expect(result.current.activeUsers.size).toBe(0);
    expect(result.current.sharedWorkspace).toBeNull();
    expect(result.current.studyGroups).toEqual([]);
  });

  it('should join room', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useCollaboration());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    result.current.joinRoom('room-123');

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'join_room',
      room_id: 'room-123',
    }));
    sendSpy.mockRestore();
  });

  it('should leave room', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useCollaboration());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    result.current.leaveRoom('room-123');

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'leave_room',
      room_id: 'room-123',
    }));
    sendSpy.mockRestore();
  });

  it('should send code changes', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useCollaboration());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    const changes = { line: 10, content: 'x = x + 1' };
    result.current.sendCodeChange('room-123', changes);

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'collaboration',
      data: expect.objectContaining({
        action: 'code_collaboration',
        room_id: 'room-123',
      }),
    }));
    sendSpy.mockRestore();
  });

  it('should update workspace', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useCollaboration());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    const workspaceData = { files: ['main.py', 'utils.py'] };
    result.current.updateWorkspace('room-123', workspaceData);

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'collaboration',
      data: expect.objectContaining({
        action: 'shared_workspace',
        room_id: 'room-123',
      }),
    }));
    sendSpy.mockRestore();
  });

  it('should join study group', async () => {
    const sendSpy = jest.spyOn(MockWebSocket.prototype, 'send');

    const { result } = renderHook(() => useCollaboration());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    result.current.joinStudyGroup('group-456');

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'collaboration',
      data: expect.objectContaining({
        action: 'study_group',
      }),
    }));
    sendSpy.mockRestore();
  });

  it('should handle user joined message', async () => {
    const { result } = renderHook(() => useCollaboration());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'user_joined',
          user_id: 'user-789',
          timestamp: '2024-02-01T10:00:00Z',
        }),
      });
    });

    expect(result.current.activeUsers.has('user-789')).toBe(true);
  });

  it('should handle user left message', async () => {
    const { result } = renderHook(() => useCollaboration());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    // User joins
    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'user_joined',
          user_id: 'user-789',
          timestamp: '2024-02-01T10:00:00Z',
        }),
      });
    });

    expect(result.current.activeUsers.has('user-789')).toBe(true);

    // User leaves
    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'user_left',
          user_id: 'user-789',
        }),
      });
    });

    expect(result.current.activeUsers.has('user-789')).toBe(false);
  });

  it('should handle workspace update', async () => {
    const { result } = renderHook(() => useCollaboration());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    const workspaceData = { files: ['main.py'], cursor: { line: 5, column: 10 } };

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'workspace_update',
          workspace_data: workspaceData,
        }),
      });
    });

    expect(result.current.sharedWorkspace).toEqual(workspaceData);
  });

  it('should handle study group joined', async () => {
    const toast = require('react-hot-toast').toast;

    const { result } = renderHook(() => useCollaboration());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    act(() => {
      mockWebSocketInstance?.onmessage?.({
        data: JSON.stringify({
          type: 'study_group_joined',
          group_id: 'Python Beginners',
        }),
      });
    });

    expect(toast.success).toHaveBeenCalledWith('Joined study group: Python Beginners');
  });
});
