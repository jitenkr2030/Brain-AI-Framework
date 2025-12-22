/**
 * Unit Tests for use-brain-ai.ts
 * Brain AI LMS - Frontend Integration Tests
 */

import { renderHook, waitFor } from '@testing-library/react';
import { useBrainRecommendations, useLearningPath, usePredictiveAnalytics, useSmartSearch, useAiTutor, useSkillAssessment } from '../use-brain-ai';

// Mock fetch globally
global.fetch = jest.fn();

describe('useBrainRecommendations', () => {
  const mockRecommendations = [
    {
      id: 'rec-1',
      courseId: 'course-1',
      courseName: 'Introduction to Neural Networks',
      reason: 'Based on your learning history',
      confidence: 0.95,
      matchPercentage: 95,
    },
    {
      id: 'rec-2',
      courseId: 'course-2',
      courseName: 'Deep Learning Fundamentals',
      reason: 'Popular among learners with similar profiles',
      confidence: 0.88,
      matchPercentage: 88,
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ recommendations: mockRecommendations }),
    });
  });

  it('should fetch recommendations on mount', async () => {
    const { result } = renderHook(() => useBrainRecommendations({
      userId: 'user-123',
      limit: 5,
    }));

    expect(result.current.isLoading).toBe(true);
    expect(result.current.recommendations).toEqual([]);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.recommendations).toEqual(mockRecommendations);
    expect(result.current.error).toBeUndefined();
  });

  it('should handle fetch error', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 500,
    });

    const { result } = renderHook(() => useBrainRecommendations({
      userId: 'user-123',
    }));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe('HTTP error! status: 500');
    expect(result.current.recommendations).toEqual([]);
  });

  it('should not fetch when disabled', () => {
    const { result } = renderHook(() => useBrainRecommendations({
      userId: 'user-123',
      enabled: false,
    }));

    expect(result.current.isLoading).toBe(false);
    expect(result.current.recommendations).toEqual([]);
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('should handle missing userId', () => {
    const { result } = renderHook(() => useBrainRecommendations({
      userId: '',
      enabled: true,
    }));

    expect(result.current.recommendations).toEqual([]);
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('should update filters correctly', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ recommendations: mockRecommendations }),
    });

    const { result, rerender } = renderHook(({ filters = {} }) => useBrainRecommendations({
      userId: 'user-123',
      filters,
    }), {
      initialProps: { filters: { category: 'ai' } },
    });

    result.current.setFilters({ category: 'ml', difficulty: 'advanced' });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });
});

describe('useLearningPath', () => {
  const mockLearningPath = {
    id: 'path-1',
    userId: 'user-123',
    targetGoal: 'Master Neural Networks',
    estimatedDuration: '3 months',
    currentSkills: { python: 80, math: 70 },
    milestones: [
      { id: 'm1', title: 'Linear Algebra Refresher', status: 'completed', duration: '1 week' },
      { id: 'm2', title: 'Neural Network Basics', status: 'in_progress', duration: '2 weeks' },
    ],
    skillGaps: ['matrix_operations', 'calculus'],
    prerequisites: ['Python Programming', 'Basic Math'],
    recommendedResources: ['Khan Academy Math', 'Python Crash Course'],
    difficulty: 'intermediate',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockLearningPath,
    });
  });

  it('should fetch learning path on mount', async () => {
    const { result } = renderHook(() => useLearningPath({
      userId: 'user-123',
      targetGoal: 'Master Neural Networks',
    }));

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.learningPath).toEqual(mockLearningPath);
    expect(result.current.error).toBeUndefined();
  });

  it('should generate new path with different goal', async () => {
    const newGoal = 'Become a Data Scientist';
    const { result } = renderHook(() => useLearningPath({
      userId: 'user-123',
      targetGoal: 'Master Neural Networks',
    }));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    result.current.generateNewPath(newGoal);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
          body: JSON.stringify({
            user_id: 'user-123',
            target_goal: newGoal,
            current_skills: {},
          }),
        })
      );
    });
  });

  it('should handle API errors', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 404,
    });

    const { result } = renderHook(() => useLearningPath({
      userId: 'user-123',
      targetGoal: 'Master Neural Networks',
    }));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe('HTTP error! status: 404');
    expect(result.current.learningPath).toBeNull();
  });
});

describe('usePredictiveAnalytics', () => {
  const mockAnalytics = {
    userId: 'user-123',
    predictedScore: 85,
    recommendedStudyTime: 120,
    atRiskCourses: [],
    strongAreas: ['python', 'machine_learning'],
    improvementAreas: ['deep_learning', 'math'],
    engagementScore: 78,
    completionProbability: 0.82,
    lastUpdated: new Date().toISOString(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockAnalytics,
    });
  });

  it('should fetch analytics on mount', async () => {
    const { result } = renderHook(() => usePredictiveAnalytics({
      userId: 'user-123',
    }));

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.analytics).toEqual(mockAnalytics);
  });

  it('should handle fetch error gracefully', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 500,
    });

    const { result } = renderHook(() => usePredictiveAnalytics({
      userId: 'user-123',
    }));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe('HTTP error! status: 500');
    expect(result.current.analytics).toBeNull();
  });

  it('should not fetch when enabled is false', () => {
    const { result } = renderHook(() => usePredictiveAnalytics({
      userId: 'user-123',
      enabled: false,
    }));

    expect(result.current.isLoading).toBe(false);
    expect(result.current.analytics).toBeNull();
    expect(global.fetch).not.toHaveBeenCalled();
  });
});

describe('useSmartSearch', () => {
  const mockSearchResults = [
    {
      id: 'res-1',
      type: 'course',
      title: 'Neural Networks Course',
      url: '/courses/neural-networks',
      snippet: 'Learn neural networks from scratch...',
      relevance: 0.95,
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ results: mockSearchResults }),
    });
  });

  it('should initialize with empty state', () => {
    const { result } = renderHook(() => useSmartSearch());

    expect(result.current.query).toBe('');
    expect(result.current.results).toEqual([]);
    expect(result.current.isSearching).toBe(false);
  });

  it('should perform search when query changes', async () => {
    const { result, rerender } = renderHook(({ query }) => useSmartSearch({ debounceMs: 0 }), {
      initialProps: { query: '' },
    });

    rerender({ query: 'neural networks' });

    await waitFor(() => {
      expect(result.current.isSearching).toBe(false);
    });

    expect(result.current.results).toEqual(mockSearchResults);
    expect(result.current.query).toBe('neural networks');
  });

  it('should clear results when query is empty', () => {
    const { result } = renderHook(() => useSmartSearch({ debounceMs: 0 }));

    // Simulate searching
    result.current.search('test');
    expect(result.current.results.length).toBeGreaterThan(0);

    // Clear
    result.current.clearResults();
    expect(result.current.results).toEqual([]);
  });

  it('should update search time after search completes', async () => {
    const { result, rerender } = renderHook(({ query }) => useSmartSearch({ debounceMs: 0 }), {
      initialProps: { query: '' },
    });

    rerender({ query: 'machine learning' });

    await waitFor(() => {
      expect(result.current.searchTime).toBeGreaterThanOrEqual(0);
    });
  });
});

describe('useAiTutor', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ response: 'Here is an explanation of neural networks...' }),
    });
  });

  it('should initialize with empty messages', () => {
    const { result } = renderHook(() => useAiTutor({
      userId: 'user-123',
    }));

    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.isTyping).toBe(false);
  });

  it('should send message and receive response', async () => {
    const { result } = renderHook(() => useAiTutor({
      userId: 'user-123',
    }));

    expect(result.current.messages).toHaveLength(0);

    result.current.sendMessage('What is a neural network?');

    await waitFor(() => {
      expect(result.current.messages).toHaveLength(2);
    });

    expect(result.current.messages[0].role).toBe('user');
    expect(result.current.messages[1].role).toBe('assistant');
  });

  it('should handle error when sending message fails', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 500,
    });

    const { result } = renderHook(() => useAiTutor({
      userId: 'user-123',
    }));

    result.current.sendMessage('What is a neural network?');

    await waitFor(() => {
      expect(result.current.error).toBe('HTTP error! status: 500');
    });
  });

  it('should clear message history', async () => {
    const { result } = renderHook(() => useAiTutor({
      userId: 'user-123',
    }));

    result.current.sendMessage('Test message');

    await waitFor(() => {
      expect(result.current.messages.length).toBeGreaterThan(0);
    });

    result.current.clearHistory();
    expect(result.current.messages).toEqual([]);
  });

  it('should not send empty messages', async () => {
    const { result } = renderHook(() => useAiTutor({
      userId: 'user-123',
    }));

    result.current.sendMessage('   ');

    expect(result.current.messages).toEqual([]);
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('should limit message history to maxHistoryLength', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ response: 'Response' }),
    });

    const { result } = renderHook(() => useAiTutor({
      userId: 'user-123',
      maxHistoryLength: 3,
    }));

    // Send multiple messages
    for (let i = 0; i < 5; i++) {
      result.current.sendMessage(`Message ${i}`);
      await waitFor(() => {
        // Allow state updates
      });
    }

    // Should have at most maxHistoryLength messages
    expect(result.current.messages.length).toBeLessThanOrEqual(3);
  });
});

describe('useSkillAssessment', () => {
  const mockAssessment = {
    id: 'assess-1',
    userId: 'user-123',
    assessmentDate: new Date().toISOString(),
    overallScore: 75,
    skillLevels: {
      python: 80,
      machine_learning: 70,
      deep_learning: 65,
    },
    recommendations: ['Consider taking Deep Learning course'],
    estimatedTimeToMastery: '2 months',
    strengthAreas: ['Python Programming'],
    growthAreas: ['Neural Network Architecture'],
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockAssessment,
    });
  });

  it('should initialize with null assessment', () => {
    const { result } = renderHook(() => useSkillAssessment({
      userId: 'user-123',
    }));

    expect(result.current.assessment).toBeNull();
    expect(result.current.isLoading).toBe(false);
  });

  it('should perform skill assessment', async () => {
    const { result } = renderHook(() => useSkillAssessment({
      userId: 'user-123',
    }));

    const assessmentResults = {
      python: 80,
      machine_learning: 70,
      deep_learning: 65,
    };

    result.current.assessSkills(assessmentResults);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.assessment).toEqual(mockAssessment);
  });

  it('should handle assessment error', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 400,
    });

    const { result } = renderHook(() => useSkillAssessment({
      userId: 'user-123',
    }));

    result.current.assessSkills({ python: 80 });

    await waitFor(() => {
      expect(result.current.error).toBe('HTTP error! status: 400');
    });
  });

  it('should not assess when disabled', () => {
    const { result } = renderHook(() => useSkillAssessment({
      userId: 'user-123',
      enabled: false,
    }));

    result.current.assessSkills({ python: 80 });
    expect(result.current.isLoading).toBe(false);
    expect(global.fetch).not.toHaveBeenCalled();
  });
});
