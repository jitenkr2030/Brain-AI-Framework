/**
 * Brain AI Hooks for LMS Frontend
 * Custom React hooks for interacting with the Brain AI framework
 */

import { useState, useEffect, useCallback } from 'react';
import type {
  CourseRecommendation,
  LearningPath,
  PredictiveAnalytics,
  SearchResult,
  TutorResponse,
  SkillAssessment,
  LoadingState,
  RecommendationFilter,
} from '@/types/brain-ai';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface UseBrainRecommendationsOptions {
  userId: string;
  limit?: number;
  enabled?: boolean;
  filters?: RecommendationFilter;
}

interface UseBrainRecommendationsReturn extends LoadingState {
  recommendations: CourseRecommendation[];
  refresh: () => Promise<void>;
  filters: RecommendationFilter;
  setFilters: (filters: RecommendationFilter) => void;
}

export function useBrainRecommendations({
  userId,
  limit = 5,
  enabled = true,
  filters = {},
}: UseBrainRecommendationsOptions): UseBrainRecommendationsReturn {
  const [recommendations, setRecommendations] = useState<CourseRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();
  const [lastUpdated, setLastUpdated] = useState<string | undefined>();
  const [currentFilters, setFilters] = useState<RecommendationFilter>(filters);

  const fetchRecommendations = useCallback(async () => {
    if (!enabled || !userId) return;

    setIsLoading(true);
    setError(undefined);

    try {
      const queryParams = new URLSearchParams({
        user_id: userId,
        limit: limit.toString(),
        ...currentFilters,
      });

      const response = await fetch(
        `${API_BASE_URL}/api/v1/brain-ai/recommendations?${queryParams}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setRecommendations(data.recommendations || []);
      setLastUpdated(new Date().toISOString());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch recommendations');
      // Set empty recommendations on error to avoid undefined
      setRecommendations([]);
    } finally {
      setIsLoading(false);
    }
  }, [userId, limit, enabled, currentFilters]);

  useEffect(() => {
    fetchRecommendations();
  }, [fetchRecommendations]);

  return {
    recommendations,
    isLoading,
    error,
    lastUpdated,
    refresh: fetchRecommendations,
    filters: currentFilters,
    setFilters: setFilters,
  };
}

interface UseLearningPathOptions {
  userId: string;
  targetGoal: string;
  currentSkills?: { [skill: string]: number };
  enabled?: boolean;
}

interface UseLearningPathReturn extends LoadingState {
  learningPath: LearningPath | null;
  generateNewPath: (newGoal?: string) => Promise<void>;
}

export function useLearningPath({
  userId,
  targetGoal,
  currentSkills = {},
  enabled = true,
}: UseLearningPathOptions): UseLearningPathReturn {
  const [learningPath, setLearningPath] = useState<LearningPath | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();

  const generatePath = useCallback(async (newGoal?: string) => {
    if (!enabled || !userId) return;

    setIsLoading(true);
    setError(undefined);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/brain-ai/learning-path`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          target_goal: newGoal || targetGoal,
          current_skills: currentSkills,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setLearningPath(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate learning path');
    } finally {
      setIsLoading(false);
    }
  }, [userId, targetGoal, currentSkills, enabled]);

  useEffect(() => {
    generatePath();
  }, [generatePath]);

  return {
    learningPath,
    isLoading,
    error,
    lastUpdated: learningPath ? new Date().toISOString() : undefined,
    generateNewPath: generatePath,
  };
}

interface UsePredictiveAnalyticsOptions {
  userId: string;
  enabled?: boolean;
  refreshInterval?: number; // in milliseconds
}

interface UsePredictiveAnalyticsReturn extends LoadingState {
  analytics: PredictiveAnalytics | null;
  refresh: () => Promise<void>;
}

export function usePredictiveAnalytics({
  userId,
  enabled = true,
  refreshInterval,
}: UsePredictiveAnalyticsOptions): UsePredictiveAnalyticsReturn {
  const [analytics, setAnalytics] = useState<PredictiveAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();

  const fetchAnalytics = useCallback(async () => {
    if (!enabled || !userId) return;

    setIsLoading(true);
    setError(undefined);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/brain-ai/analytics?user_id=${userId}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics');
      setAnalytics(null);
    } finally {
      setIsLoading(false);
    }
  }, [userId, enabled]);

  useEffect(() => {
    fetchAnalytics();

    if (refreshInterval) {
      const interval = setInterval(fetchAnalytics, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchAnalytics, refreshInterval]);

  return {
    analytics,
    isLoading,
    error,
    lastUpdated: analytics ? new Date().toISOString() : undefined,
    refresh: fetchAnalytics,
  };
}

interface UseSmartSearchOptions {
  userContext?: {
    userId: string;
    currentCourse?: string;
    currentModule?: string;
  };
  debounceMs?: number;
}

interface UseSmartSearchReturn {
  query: string;
  results: SearchResult[];
  isSearching: boolean;
  searchTime: number;
  setQuery: (query: string) => void;
  search: (query: string) => Promise<void>;
  clearResults: () => void;
}

export function useSmartSearch({
  userContext,
  debounceMs = 300,
}: UseSmartSearchOptions = {}): UseSmartSearchReturn {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchTime, setSearchTime] = useState(0);

  const performSearch = useCallback(async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setIsSearching(true);
    const startTime = Date.now();

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/brain-ai/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          user_context: userContext,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data.results || []);
      setSearchTime(Date.now() - startTime);
    } catch (err) {
      console.error('Search error:', err);
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  }, [userContext]);

  useEffect(() => {
    if (debounceMs > 0 && query) {
      const debounceTimer = setTimeout(() => {
        performSearch(query);
      }, debounceMs);

      return () => clearTimeout(debounceTimer);
    }
  }, [query, debounceMs, performSearch]);

  return {
    query,
    results,
    isSearching,
    searchTime,
    setQuery,
    search: performSearch,
    clearResults: () => setResults([]),
  };
}

interface UseAiTutorOptions {
  userId: string;
  initialContext?: {
    currentContent?: string;
    currentCourse?: string;
  };
  maxHistoryLength?: number;
}

interface UseAiTutorReturn extends LoadingState {
  messages: Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  }>;
  isTyping: boolean;
  sendMessage: (message: string) => Promise<void>;
  clearHistory: () => void;
}

export function useAiTutor({
  userId,
  initialContext,
  maxHistoryLength = 50,
}: UseAiTutorOptions): UseAiTutorReturn {
  const [messages, setMessages] = useState<Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  }>>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();
  const [isTyping, setIsTyping] = useState(false);

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;

    const userMessage = {
      id: `msg-${Date.now()}-user`,
      role: 'user' as const,
      content: message,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage].slice(-maxHistoryLength));
    setIsLoading(true);
    setIsTyping(true);
    setError(undefined);

    try {
      const conversationHistory = messages.map(({ role, content }) => ({
        role,
        content,
      }));

      const response = await fetch(`${API_BASE_URL}/api/v1/brain-ai/tutor`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          conversation_history: conversationHistory,
          current_content: initialContext?.currentContent || '',
          question: message,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage = {
        id: `msg-${Date.now()}-assistant`,
        role: 'assistant' as const,
        content: data.response,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage].slice(-maxHistoryLength));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get tutor response');
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  }, [userId, messages, initialContext, maxHistoryLength]);

  const clearHistory = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isLoading,
    error,
    isTyping,
    sendMessage,
    clearHistory,
  };
}

interface UseSkillAssessmentOptions {
  userId: string;
  enabled?: boolean;
}

interface UseSkillAssessmentReturn extends LoadingState {
  assessment: SkillAssessment | null;
  assessSkills: (assessmentResults: { [skill: string]: number }) => Promise<void>;
}

export function useSkillAssessment({
  userId,
  enabled = true,
}: UseSkillAssessmentOptions): UseSkillAssessmentReturn {
  const [assessment, setAssessment] = useState<SkillAssessment | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();

  const performAssessment = useCallback(async (assessmentResults: { [skill: string]: number }) => {
    if (!enabled || !userId) return;

    setIsLoading(true);
    setError(undefined);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/brain-ai/skills/assess`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          assessment_results: assessmentResults,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setAssessment(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to assess skills');
    } finally {
      setIsLoading(false);
    }
  }, [userId, enabled]);

  return {
    assessment,
    isLoading,
    error,
    assessSkills: performAssessment,
  };
}
