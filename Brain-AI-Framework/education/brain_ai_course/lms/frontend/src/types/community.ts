"""
Frontend TypeScript types for Brain AI LMS Community Features
Phase 3: Revenue Optimization - Community Features
"""

export interface Event {
  id: number;
  title: string;
  description?: string;
  event_type: 'webinar' | 'workshop' | 'conference' | 'networking' | 'q_and_a' | 'study_session';
  status: 'draft' | 'published' | 'live' | 'completed' | 'cancelled';
  start_datetime: string;
  end_datetime: string;
  timezone: string;
  max_attendees?: number;
  current_attendees: number;
  registration_required: boolean;
  registration_deadline?: string;
  meeting_url?: string;
  recording_url?: string;
  materials_url?: string;
  speaker_bio?: string;
  prerequisites?: string;
  tags?: string; // JSON array
  is_featured: boolean;
  created_by: number;
  created_at: string;
  updated_at?: string;
}

export interface EventRegistration {
  id: number;
  event_id: number;
  user_id: number;
  registration_date: string;
  attendance_confirmed: boolean;
  feedback_rating?: number; // 1-5 scale
  feedback_comment?: string;
  certificate_issued: boolean;
  certificate_url?: string;
}

export interface StudyGroup {
  id: number;
  name: string;
  description?: string;
  privacy_level: 'public' | 'private' | 'invite_only';
  status: 'active' | 'paused' | 'completed' | 'cancelled';
  max_members: number;
  current_members: number;
  subject_area?: string;
  meeting_schedule?: string;
  next_meeting_date?: string;
  meeting_location?: string;
  group_image_url?: string;
  tags?: string; // JSON array
  created_by: number;
  created_at: string;
  updated_at?: string;
}

export interface StudyGroupMember {
  id: number;
  study_group_id: number;
  user_id: number;
  role: 'member' | 'moderator' | 'admin';
  joined_date: string;
  contribution_score: number;
  is_active: boolean;
}

export interface StudySession {
  id: number;
  study_group_id: number;
  title: string;
  description?: string;
  scheduled_start: string;
  scheduled_end: string;
  actual_start?: string;
  actual_end?: string;
  meeting_url?: string;
  recording_url?: string;
  agenda?: string;
  notes?: string;
  attendance_count: number;
  created_by: number;
  created_at: string;
}

export interface StudySessionAttendance {
  id: number;
  session_id: number;
  user_id: number;
  joined_at?: string;
  left_at?: string;
  participation_score: number;
}

export interface OfficeHour {
  id: number;
  expert_id: number;
  title: string;
  description?: string;
  office_hour_type: 'group' | 'one_on_one' | 'mentorship';
  scheduled_date: string;
  duration_minutes: number;
  max_participants: number;
  current_participants: number;
  topics?: string; // JSON array
  meeting_url?: string;
  status: 'scheduled' | 'live' | 'completed' | 'cancelled';
  recording_url?: string;
  created_at: string;
}

export interface OfficeHourRegistration {
  id: number;
  office_hour_id: number;
  user_id: number;
  topics_of_interest?: string; // JSON array
  registration_date: string;
  attendance_confirmed: boolean;
  feedback_rating?: number; // 1-5 scale
  feedback_comment?: string;
}

export interface AlumniProfile {
  id: number;
  user_id: number;
  graduation_date?: string;
  current_job_title?: string;
  current_company?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  github_url?: string;
  twitter_url?: string;
  bio?: string;
  expertise_areas?: string; // JSON array
  availability_for_mentoring: boolean;
  willingness_to_speak: boolean;
  status: 'active' | 'inactive' | 'mentor' | 'speaker';
  career_highlights?: string;
  networking_interests?: string; // JSON array
  profile_completeness_score: number;
  created_at: string;
  updated_at?: string;
}

export interface AlumniConnection {
  id: number;
  alumni_profile_id: number;
  connected_user_id: number;
  connection_type: 'network' | 'mentorship' | 'collaboration';
  status: 'pending' | 'accepted' | 'declined';
  message?: string;
  created_at: string;
  connected_at?: string;
}

export interface JobOpportunity {
  id: number;
  posted_by: number;
  title: string;
  company: string;
  location?: string;
  employment_type?: 'full-time' | 'part-time' | 'contract' | 'freelance';
  experience_level?: 'entry' | 'mid' | 'senior' | 'lead';
  salary_range_min?: number;
  salary_range_max?: number;
  currency: string;
  description?: string;
  requirements?: string;
  application_url?: string;
  application_deadline?: string;
  is_remote: boolean;
  tags?: string; // JSON array
  status: 'active' | 'filled' | 'expired';
  views_count: number;
  applications_count: number;
  created_at: string;
  updated_at?: string;
}

export interface JobApplication {
  id: number;
  job_opportunity_id: number;
  applicant_id: number;
  cover_letter?: string;
  resume_url?: string;
  portfolio_url?: string;
  status: 'pending' | 'reviewed' | 'interview' | 'offer' | 'rejected';
  application_date: string;
  updated_at?: string;
}

export interface CommunityDashboard {
  total_events_this_month: number;
  active_study_groups: number;
  upcoming_office_hours: number;
  active_alumni: number;
  job_opportunities_posted: number;
  study_group_participants: number;
  event_registrations: number;
  office_hour_attendance: number;
}

export interface EventAnalytics {
  event_id: number;
  title: string;
  total_registrations: number;
  actual_attendance: number;
  attendance_rate: number;
  average_feedback_rating: number;
  total_feedback_count: number;
  certificates_issued: number;
}

export interface StudyGroupAnalytics {
  study_group_id: number;
  name: string;
  total_members: number;
  active_members: number;
  sessions_held: number;
  average_attendance: number;
  completion_rate: number;
}

export interface AlumniNetworkAnalytics {
  total_alumni: number;
  active_alumni: number;
  available_mentors: number;
  willing_speakers: number;
  profile_completeness_average: number;
  recent_graduates: number;
  job_placement_rate: number;
}

export interface CommunityMetrics {
  eventsThisMonth: number;
  activeStudyGroups: number;
  upcomingOfficeHours: number;
  activeAlumni: number;
  jobOpportunities: number;
  totalParticipants: number;
}

export interface EventFormData {
  title: string;
  description?: string;
  event_type: Event['event_type'];
  start_datetime: string;
  end_datetime: string;
  timezone: string;
  max_attendees?: number;
  registration_required: boolean;
  registration_deadline?: string;
  meeting_url?: string;
  materials_url?: string;
  speaker_bio?: string;
  prerequisites?: string;
  tags?: string[];
  is_featured: boolean;
}

export interface StudyGroupFormData {
  name: string;
  description?: string;
  privacy_level: StudyGroup['privacy_level'];
  max_members: number;
  subject_area?: string;
  meeting_schedule?: string;
  next_meeting_date?: string;
  meeting_location?: string;
  group_image_url?: string;
  tags?: string[];
}

export interface OfficeHourFormData {
  title: string;
  description?: string;
  office_hour_type: OfficeHour['office_hour_type'];
  scheduled_date: string;
  duration_minutes: number;
  max_participants: number;
  topics?: string[];
  meeting_url?: string;
}

export interface AlumniProfileFormData {
  graduation_date?: string;
  current_job_title?: string;
  current_company?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  github_url?: string;
  twitter_url?: string;
  bio?: string;
  expertise_areas?: string[];
  availability_for_mentoring: boolean;
  willingness_to_speak: boolean;
  career_highlights?: string;
  networking_interests?: string[];
}

export interface JobOpportunityFormData {
  title: string;
  company: string;
  location?: string;
  employment_type?: JobOpportunity['employment_type'];
  experience_level?: JobOpportunity['experience_level'];
  salary_range_min?: number;
  salary_range_max?: number;
  currency: string;
  description?: string;
  requirements?: string;
  application_url?: string;
  application_deadline?: string;
  is_remote: boolean;
  tags?: string[];
}

export interface StudyGroupInvite {
  email: string;
  role: 'member' | 'moderator' | 'admin';
  message?: string;
}

export interface EventFeedback {
  event_id: number;
  rating: number; // 1-5
  comment?: string;
  would_recommend: boolean;
  topics_covered: string[];
  difficulty_level: 'too_easy' | 'just_right' | 'too_hard';
}

export interface OfficeHourFeedback {
  office_hour_id: number;
  rating: number; // 1-5
  comment?: string;
  questions_answered: boolean;
  follow_up_needed: boolean;
}

export interface AlumniReferral {
  referred_user_id: number;
  referral_program: string;
  status: 'pending' | 'completed' | 'rewarded';
  reward_amount?: number;
  created_at: string;
}

export interface CommunityNotification {
  id: number;
  type: 'event_reminder' | 'study_group_update' | 'office_hour_announcement' | 'alumni_connection' | 'job_opportunity';
  title: string;
  message: string;
  is_read: boolean;
  action_url?: string;
  created_at: string;
  expires_at?: string;
}

export interface CommunitySearchFilters {
  event_type?: Event['event_type'];
  study_group_privacy?: StudyGroup['privacy_level'];
  office_hour_type?: OfficeHour['office_hour_type'];
  alumni_expertise?: string[];
  job_employment_type?: JobOpportunity['employment_type'];
  date_range?: {
    start: string;
    end: string;
  };
  location?: string;
  is_remote?: boolean;
}

export interface CommunityEngagementMetrics {
  period_days: number;
  events_attended: number;
  study_groups_joined: number;
  office_hours_attended: number;
  alumni_connections_made: number;
  jobs_applied: number;
  total_participation_score: number;
  streak_days: number;
}