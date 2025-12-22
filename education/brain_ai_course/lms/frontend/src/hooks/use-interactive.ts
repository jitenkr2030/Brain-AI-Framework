"""
Interactive Learning Hooks
React hooks for managing WebSocket connections and state for interactive features
"""

import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from './use-auth';
import { toast } from 'react-hot-toast';
import type {
  CodeExecutionRequest,
  CodeExecutionResult,
  TutorMessage,
  PeerReviewSubmission,
  MentorshipSession
} from '@/types/interactive';

export function useWebSocket() {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionId, setConnectionId] = useState<string | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const { user } = useAuth();

  const connect = useCallback(() => {
    if (!user?.token || isConnected) return;

    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/interactive?token=${user.token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setIsConnected(true);
      setSocket(ws);
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleWebSocketMessage(message);
    };

    ws.onclose = () => {
      setIsConnected(false);
      setSocket(null);
      setConnectionId(null);
      
      // Attempt to reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 3000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      toast.error('Connection error. Retrying...');
    };

  }, [user?.token, isConnected]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (socket) {
      socket.close();
    }
  }, [socket]);

  const sendMessage = useCallback((message: any) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    }
  }, [socket, isConnected]);

  useEffect(() => {
    connect();
    return disconnect;
  }, [connect, disconnect]);

  return {
    socket,
    isConnected,
    connectionId,
    sendMessage,
    connect,
    disconnect
  };
}

export function useCodeExecution() {
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionHistory, setExecutionHistory] = useState<CodeExecutionResult[]>([]);
  const [currentExecution, setCurrentExecution] = useState<CodeExecutionResult | null>(null);
  const { sendMessage, isConnected } = useWebSocket();

  const executeCode = useCallback(async (request: CodeExecutionRequest) => {
    if (!isConnected) {
      toast.error('Not connected to execution server');
      return;
    }

    setIsExecuting(true);
    
    const message = {
      type: 'code_execution',
      data: request
    };

    sendMessage(message);
  }, [sendMessage, isConnected]);

  const handleExecutionMessage = useCallback((message: any) => {
    if (message.type === 'code_execution_start') {
      const execution: CodeExecutionResult = {
        executionId: message.execution_id,
        status: 'pending',
        output: '',
        executionTime: 0,
        stdout: '',
        stderr: '',
        timestamp: new Date().toISOString()
      };
      setCurrentExecution(execution);
    } else if (message.type === 'execution_output') {
      setCurrentExecution(prev => prev ? {
        ...prev,
        output: prev.output + message.output + '\n',
        stdout: prev.stdout + message.output + '\n'
      } : null);
    } else if (message.type === 'execution_complete') {
      const result: CodeExecutionResult = {
        executionId: message.execution_id,
        status: message.status,
        output: message.output,
        error: message.error,
        executionTime: message.execution_time,
        stdout: message.stdout,
        stderr: message.stderr,
        timestamp: new Date().toISOString()
      };
      
      setCurrentExecution(result);
      setExecutionHistory(prev => [result, ...prev]);
      setIsExecuting(false);
      
      if (message.error) {
        toast.error(`Execution failed: ${message.error}`);
      } else {
        toast.success('Code executed successfully!');
      }
    } else if (message.type === 'execution_error') {
      setIsExecuting(false);
      toast.error(`Execution error: ${message.error}`);
    }
  }, []);

  return {
    executeCode,
    isExecuting,
    executionHistory,
    currentExecution,
    handleExecutionMessage
  };
}

export function useAITutor() {
  const [messages, setMessages] = useState<TutorMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const { sendMessage, isConnected } = useWebSocket();

  const sendMessageToTutor = useCallback(async (question: string, context?: any) => {
    if (!isConnected) {
      toast.error('AI tutor is not available');
      return;
    }

    // Add user message
    const userMessage: TutorMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: question,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    const message = {
      type: 'ai_tutor_chat',
      data: {
        question,
        conversation_id: conversationId,
        ...context
      }
    };

    sendMessage(message);
  }, [sendMessage, isConnected, conversationId]);

  const handleTutorResponse = useCallback((message: any) => {
    if (message.type === 'ai_tutor_response') {
      const response = message.data;
      
      const assistantMessage: TutorMessage = {
        id: response.query_id,
        type: 'assistant',
        content: response.response,
        codeExample: response.code_example,
        resources: response.resources,
        timestamp: response.timestamp
      };

      setMessages(prev => [...prev, assistantMessage]);
      setConversationId(response.query_id);
      setIsTyping(false);
    }
  }, []);

  const clearConversation = useCallback(() => {
    setMessages([]);
    setConversationId(null);
  }, []);

  return {
    messages,
    isTyping,
    conversationId,
    sendMessageToTutor,
    handleTutorResponse,
    clearConversation
  };
}

export function usePeerReview() {
  const [submissions, setSubmissions] = useState<PeerReviewSubmission[]>([]);
  const [pendingReviews, setPendingReviews] = useState<PeerReviewSubmission[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { sendMessage, isConnected } = useWebSocket();

  const submitForReview = useCallback(async (submission: {
    lessonId: number;
    title: string;
    description: string;
    code: string;
    language: string;
  }) => {
    if (!isConnected) {
      toast.error('Peer review service is not available');
      return;
    }

    setIsLoading(true);

    const message = {
      type: 'peer_review',
      data: {
        action: 'submit_code',
        ...submission
      }
    };

    sendMessage(message);
  }, [sendMessage, isConnected]);

  const submitFeedback = useCallback(async (reviewRequestId: string, feedback: {
    overallScore: number;
    detailedFeedback: any;
    strengths: string[];
    improvements: string[];
  }) => {
    if (!isConnected) {
      toast.error('Peer review service is not available');
      return;
    }

    const message = {
      type: 'peer_review',
      data: {
        action: 'submit_feedback',
        review_request_id: reviewRequestId,
        ...feedback
      }
    };

    sendMessage(message);
  }, [sendMessage, isConnected]);

  const getSubmissionReviews = useCallback(async (submissionId: string) => {
    if (!isConnected) {
      toast.error('Peer review service is not available');
      return;
    }

    const message = {
      type: 'peer_review',
      data: {
        action: 'get_reviews',
        submission_id: submissionId
      }
    };

    sendMessage(message);
  }, [sendMessage, isConnected]);

  const handlePeerReviewMessage = useCallback((message: any) => {
    if (message.type === 'peer_review_submitted') {
      const result = message.data;
      if (result.success) {
        toast.success('Code submitted for review successfully!');
        // Add to submissions list
        setSubmissions(prev => [{
          submissionId: result.submission_id,
          title: message.data.title,
          description: message.data.description,
          code: message.data.code,
          language: message.data.language,
          status: 'pending',
          reviewers: []
        }, ...prev]);
      } else {
        toast.error(result.error || 'Failed to submit for review');
      }
      setIsLoading(false);
    } else if (message.type === 'peer_review_feedback_submitted') {
      const result = message.data;
      if (result.success) {
        toast.success('Feedback submitted successfully!');
      } else {
        toast.error(result.error || 'Failed to submit feedback');
      }
    } else if (message.type === 'peer_review_data') {
      // Handle reviews data
      console.log('Reviews data:', message.data);
    }
  }, []);

  const getReviewerDashboard = useCallback(async () => {
    if (!isConnected) {
      toast.error('Peer review service is not available');
      return;
    }

    const message = {
      type: 'peer_review',
      data: {
        action: 'get_dashboard'
      }
    };

    sendMessage(message);
  }, [sendMessage, isConnected]);

  return {
    submissions,
    pendingReviews,
    isLoading,
    submitForReview,
    submitFeedback,
    getSubmissionReviews,
    getReviewerDashboard,
    handlePeerReviewMessage
  };
}

export function useMentorship() {
  const [mentors, setMentors] = useState<any[]>([]);
  const [mentorshipSessions, setMentorshipSessions] = useState<MentorshipSession[]>([]);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { sendMessage, isConnected } = useWebSocket();

  const findMentors = useCallback(async (criteria: {
    expertiseAreas: string[];
    sessionType: string;
    budget?: number;
    timezone?: string;
  }) => {
    if (!isConnected) {
      toast.error('Mentorship service is not available');
      return;
    }

    setIsLoading(true);

    const message = {
      type: 'mentorship',
      data: {
        action: 'find_mentors',
        ...criteria
      }
    };

    sendMessage(message);
  }, [sendMessage, isConnected]);

  const requestMentorship = useCallback(async (request: {
    expertiseAreas: string[];
    goals: string[];
    sessionType: string;
    durationMinutes?: number;
    preferredMentorId?: number;
    budget?: number;
  }) => {
    if (!isConnected) {
      toast.error('Mentorship service is not available');
      return;
    }

    setIsLoading(true);

    const message = {
      type: 'mentorship',
      data: {
        action: 'request_session',
        ...request
      }
    };

    sendMessage(message);
  }, [sendMessage, isConnected]);

  const getDashboard = useCallback(async (dashboardType: 'mentor' | 'mentee' = 'mentee') => {
    if (!isConnected) {
      toast.error('Mentorship service is not available');
      return;
    }

    const message = {
      type: 'mentorship',
      data: {
        action: 'get_dashboard',
        dashboard_type: dashboardType
      }
    };

    sendMessage(message);
  }, [sendMessage, isConnected]);

  const handleMentorshipMessage = useCallback((message: any) => {
    if (message.type === 'mentor_search_results') {
      const result = message.data;
      if (result.success) {
        setMentors(result.mentors);
      } else {
        toast.error(result.error || 'Failed to find mentors');
      }
      setIsLoading(false);
    } else if (message.type === 'mentorship_requested') {
      const result = message.data;
      if (result.success) {
        toast.success('Mentorship request submitted successfully!');
      } else {
        toast.error(result.error || 'Failed to request mentorship');
      }
      setIsLoading(false);
    } else if (message.type === 'mentorship_dashboard') {
      const result = message.data;
      if (result.success) {
        setDashboardData(result);
        setMentorshipSessions(result.upcoming_sessions || []);
      }
    }
  }, []);

  return {
    mentors,
    mentorshipSessions,
    dashboardData,
    isLoading,
    findMentors,
    requestMentorship,
    getDashboard,
    handleMentorshipMessage
  };
}

export function useCollaboration() {
  const [activeUsers, setActiveUsers] = useState<Map<string, any>>(new Map());
  const [sharedWorkspace, setSharedWorkspace] = useState<any>(null);
  const [studyGroups, setStudyGroups] = useState<any[]>([]);
  const { sendMessage, isConnected } = useWebSocket();

  const joinRoom = useCallback((roomId: string) => {
    if (!isConnected) return;

    const message = {
      type: 'join_room',
      room_id: roomId
    };

    sendMessage(message);
  }, [sendMessage, isConnected]);

  const leaveRoom = useCallback((roomId: string) => {
    if (!isConnected) return;

    const message = {
      type: 'leave_room',
      room_id: roomId
    };

    sendMessage(message);
  }, [sendMessage, isConnected]);

  const sendCodeChange = useCallback((roomId: string, changes: any) => {
    if (!isConnected) return;

    const message = {
      type: 'collaboration',
      data: {
        action: 'code_collaboration',
        room_id: roomId,
        changes
      }
    };

    sendMessage(message);
  }, [sendMessage, isConnected]);

  const updateWorkspace = useCallback((roomId: string, workspaceData: any) => {
    if (!isConnected) return;

    const message = {
      type: 'collaboration',
      data: {
        action: 'shared_workspace',
        room_id: roomId,
        workspace_data: workspaceData
      }
    };

    sendMessage(message);
  }, [sendMessage, isConnected]);

  const joinStudyGroup = useCallback((groupId: string) => {
    if (!isConnected) return;

    const message = {
      type: 'collaboration',
      data: {
        action: 'study_group',
        study_group: {
          action: 'join',
          group_id: groupId
        }
      }
    };

    sendMessage(message);
  }, [sendMessage, isConnected]);

  const handleCollaborationMessage = useCallback((message: any) => {
    if (message.type === 'user_joined') {
      setActiveUsers(prev => new Map(prev.set(message.user_id, {
        id: message.user_id,
        joinedAt: message.timestamp
      })));
    } else if (message.type === 'user_left') {
      setActiveUsers(prev => {
        const newMap = new Map(prev);
        newMap.delete(message.user_id);
        return newMap;
      });
    } else if (message.type === 'code_change') {
      // Handle code changes from other users
      console.log('Code change from user:', message.user_id, message.changes);
    } else if (message.type === 'workspace_update') {
      setSharedWorkspace(message.workspace_data);
    } else if (message.type === 'study_group_joined') {
      toast.success(`Joined study group: ${message.group_id}`);
    }
  }, []);

  return {
    activeUsers,
    sharedWorkspace,
    studyGroups,
    joinRoom,
    leaveRoom,
    sendCodeChange,
    updateWorkspace,
    joinStudyGroup,
    handleCollaborationMessage
  };
}