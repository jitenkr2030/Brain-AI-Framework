/**
 * Brain AI Framework TypeScript Types
 * Type definitions for all Brain AI related data structures
 */

// ============ Enums ============

export enum ContentType {
  VIDEO_LECTURE = 'video_lecture',
  TEXT_MODULE = 'text_module',
  QUIZ = 'quiz',
  ASSIGNMENT = 'assignment',
  DISCUSSION = 'discussion',
  COURSE = 'course',
}

export enum RecommendationInteractionType {
  VIEWED = 'viewed',
  CLICKED = 'clicked',
  ENROLLED = 'enrolled',
  DISMISSED = 'dismissed',
}

export enum LearningPathStatus {
  NOT_STARTED = 'not_started',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
}

export enum DifficultyLevel {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
}

export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
}

export enum EngagementTrend {
  INCREASING = 'increasing',
  STABLE = 'stable',
  DECLINING = 'declining',
}

export enum PredictedDifficulty {
  EASY = 'easy',
  MODERATE = 'moderate',
  CHALLENGING = 'challenging',
}

// ============ Search Types ============

export interface SearchResult {
  result_id: string;
  type: ContentType | string;
  title: string;
  snippet: string;
  relevance_score: number;
  course?: string;
  module?: string;
  url?: string;
  timestamp?: string;
}

export interface SearchFilters {
  types?: ContentType[];
  courses?: string[];
  dateRange?: {
    start: string;
    end: string;
  };
}

export interface SearchSuggestion {
  query: string;
  count: number;
}

// ============ Recommendation Types ============

export interface CourseRecommendation {
  course_id: string;
  title: string;
  instructor: string;
  category?: string;
  duration?: string;
  rating?: number;
  match_score: number;
  reasoning?: string;
  prerequisites: string[];
  skills_gained: string[];
  thumbnail?: string;
  description?: string;
  difficulty?: DifficultyLevel;
}

export interface RecommendationFilter {
  categories?: string[];
  difficulty?: DifficultyLevel;
  duration_max?: string;
  rating_min?: number;
  instructor_id?: string;
}

export interface RecommendationInteraction {
  user_id: string;
  course_id: string;
  interaction_type: RecommendationInteractionType;
  timestamp: string;
}

// ============ Learning Path Types ============

export interface LearningPathModule {
  module_id: string;
  title: string;
  description: string;
  duration: string;
  rationale: string;
  order: number;
  status?: LearningPathStatus;
  prerequisites: string[];
  resources?: string[];
  estimated_time?: string;
  skills_covered?: string[];
}

export interface LearningPath {
  path_id: string;
  user_id: string;
  target_goal: string;
  modules: LearningPathModule[];
  total_modules: number;
  estimated_duration: string;
  created_at: string;
  updated_at: string;
  current_skills?: { [skill: string]: number };
  target_skills?: string[];
}

export interface LearningPathProgress {
  path_id: string;
  completed_modules: string[];
  current_module_id?: string;
  progress_percentage: number;
  time_spent: string;
  last_activity: string;
}

// ============ AI Tutor Types ============

export interface TutorMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface TutorResponse {
  response: string;
  conversation_id: string;
  suggested_topics: string[];
  related_resources: Array<{
    title: string;
    url: string;
    type: string;
  }>;
}

export interface TutorContext {
  currentContent?: string;
  currentCourse?: string;
  currentModule?: string;
  enrolledCourses?: string[];
  completedModules?: string[];
}

export interface ConversationHistory {
  conversation_id: string;
  messages: TutorMessage[];
  created_at: string;
  updated_at: string;
}

// ============ Analytics Types ============

export interface PredictiveAnalytics {
  user_id: string;
  predicted_completion_date?: string;
  course_success_probability: number;
  risk_level: RiskLevel;
  recommended_interventions: string[];
  engagement_trend: EngagementTrend;
  predicted_difficulty: PredictedDifficulty;
  personalized_tips: string[];
}

export interface EngagementMetric {
  user_id: string;
  metric_type: string;
  value: number;
  metadata?: Record<string, unknown>;
  timestamp: string;
}

export interface CourseAnalytics {
  course_id: string;
  total_enrolled: number;
  average_completion_rate: number;
  average_time_to_complete: string;
  drop_off_points: Array<{
    module_id: string;
    drop_off_rate: number;
  }>;
  average_score: number;
}

// ============ Skill Assessment Types ============

export interface SkillAssessment {
  assessment_id: string;
  user_id: string;
  skills: { [skill: string]: number };
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  assessed_at: string;
}

export interface SkillGapAnalysis {
  user_id: string;
  target_role: string;
  current_skills: { [skill: string]: number };
  required_skills: { [skill: string]: number };
  skill_gaps: Array<{
    skill: string;
    current_level: number;
    required_level: number;
    gap: number;
    recommended_courses: string[];
  }>;
  overall_readiness: number;
}

export interface SkillDefinition {
  skill_id: string;
  name: string;
  description: string;
  category: string;
  related_skills: string[];
  difficulty_level: DifficultyLevel;
  keywords: string[];
}

// ============ Content Enhancement Types ============

export interface ContentSummary {
  content_id: string;
  summary: string;
  key_points: string[];
  estimated_read_time: string;
}

export interface KeyConcept {
  term: string;
  definition: string;
  examples: string[];
  related_concepts: string[];
}

export interface QuizQuestion {
  question_id: string;
  question: string;
  type: 'multiple_choice' | 'true_false' | 'short_answer';
  options?: string[];
  correct_answer: string | number;
  explanation: string;
  difficulty: DifficultyLevel;
  points: number;
}

export interface QuizGenerationRequest {
  content: string;
  num_questions: number;
  difficulty: DifficultyLevel;
  include_explanations: boolean;
}

export interface QuizGenerationResponse {
  questions: QuizQuestion[];
  total_points: number;
  estimated_time: string;
}

// ============ API Response Types ============

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface LoadingState {
  isLoading: boolean;
  error?: string;
  lastUpdated?: string;
}

// ============ User Context Types ============

export interface UserContext {
  userId: string;
  currentCourse?: string;
  currentModule?: string;
  enrolledCourses?: string[];
  completedCourses?: string[];
  skillLevels?: { [skill: string]: number };
  learningGoals?: string[];
  preferences?: UserPreferences;
}

export interface UserPreferences {
  preferred_difficulty?: DifficultyLevel;
  learning_pace?: 'slow' | 'moderate' | 'fast';
  preferred_content_types?: ContentType[];
  daily_study_goal?: number;
  notifications_enabled?: boolean;
}

// ============ Event Types for Tracking ============

export interface AiFeatureEvent {
  event_type: string;
  feature_name: string;
  user_id: string;
  properties?: Record<string, unknown>;
  timestamp: string;
}

export interface RecommendationViewEvent extends AiFeatureEvent {
  event_type: 'recommendation_viewed';
  recommendation_id: string;
  position: number;
  course_id: string;
}

export interface SearchEvent extends AiFeatureEvent {
  event_type: 'search_performed';
  query: string;
  results_count: number;
  selected_result?: string;
  search_time_ms: number;
}

export interface TutorInteractionEvent extends AiFeatureEvent {
  event_type: 'tutor_interaction';
  conversation_id: string;
  message_count: number;
  satisfaction_rating?: number;
}
