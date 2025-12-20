"""
Frontend Components for Interactive Learning Features
React components for code execution, AI tutor chat, peer review, and collaboration
"""

# This file would contain the React TypeScript components
# For brevity, I'm creating the component structure and key functionality

export interface CodeExecutionRequest {
  code: string;
  language: string;
  lessonId: number;
  dependencies?: string[];
  timeout?: number;
  memoryLimit?: number;
  cpuLimit?: number;
}

export interface CodeExecutionResult {
  executionId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'timeout';
  output: string;
  error?: string;
  executionTime: number;
  stdout: string;
  stderr: string;
  timestamp: string;
}

export interface TutorMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  codeExample?: string;
  resources?: Array<{
    title: string;
    url: string;
    type: string;
  }>;
  timestamp: string;
}

export interface PeerReviewSubmission {
  submissionId: string;
  title: string;
  description: string;
  code: string;
  language: string;
  status: 'pending' | 'in_review' | 'approved' | 'changes_requested';
  reviewers: Array<{
    id: number;
    name: string;
    feedback?: {
      overallScore: number;
      strengths: string[];
      improvements: string[];
    };
  }>;
}

export interface MentorshipSession {
  sessionId: string;
  mentorId: number;
  mentorName: string;
  menteeId: number;
  sessionType: 'one_on_one' | 'group_session' | 'code_review' | 'career_advice';
  scheduledAt: string;
  durationMinutes: number;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  agenda: string[];
  notes?: string;
}