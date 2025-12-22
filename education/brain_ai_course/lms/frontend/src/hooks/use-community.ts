"""
Frontend React hooks for Brain AI LMS Community Features
Phase 3: Revenue Optimization - Community Features
"""

'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  Event,
  EventRegistration,
  StudyGroup,
  StudyGroupMember,
  StudySession,
  StudySessionAttendance,
  OfficeHour,
  OfficeHourRegistration,
  AlumniProfile,
  AlumniConnection,
  JobOpportunity,
  JobApplication,
  CommunityDashboard,
  EventAnalytics,
  StudyGroupAnalytics,
  AlumniNetworkAnalytics,
  EventFormData,
  StudyGroupFormData,
  OfficeHourFormData,
  AlumniProfileFormData,
  JobOpportunityFormData,
  CommunitySearchFilters,
  CommunityEngagementMetrics
} from '@/types/community';

// Base API configuration
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Events Hook
export function useEvents() {
  const [events, setEvents] = useState<Event[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEvents = useCallback(async (filters?: Partial<CommunitySearchFilters>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      if (filters?.event_type) params.append('event_type', filters.event_type);
      if (filters?.date_range) {
        params.append('start_date', filters.date_range.start);
        params.append('end_date', filters.date_range.end);
      }
      params.append('upcoming_only', 'true');
      
      const response = await fetch(`${API_BASE}/community/events?${params}`);
      if (!response.ok) throw new Error('Failed to fetch events');
      
      const data = await response.json();
      setEvents(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createEvent = useCallback(async (eventData: EventFormData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/events`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(eventData),
      });
      
      if (!response.ok) throw new Error('Failed to create event');
      
      const data = await response.json();
      setEvents(prev => [...prev, data]);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateEvent = useCallback(async (eventId: number, updateData: Partial<EventFormData>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/events/${eventId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData),
      });
      
      if (!response.ok) throw new Error('Failed to update event');
      
      const data = await response.json();
      setEvents(prev => prev.map(e => e.id === eventId ? data : e));
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const registerForEvent = useCallback(async (eventId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/events/${eventId}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event_id: eventId }),
      });
      
      if (!response.ok) throw new Error('Failed to register for event');
      
      const data = await response.json();
      // Refresh events to update attendee count
      await fetchEvents();
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [fetchEvents]);

  const confirmAttendance = useCallback(async (eventId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/events/${eventId}/attendance`, {
        method: 'POST',
      });
      
      if (!response.ok) throw new Error('Failed to confirm attendance');
      
      const data = await response.json();
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    events,
    isLoading,
    error,
    fetchEvents,
    createEvent,
    updateEvent,
    registerForEvent,
    confirmAttendance,
  };
}

// Study Groups Hook
export function useStudyGroups() {
  const [studyGroups, setStudyGroups] = useState<StudyGroup[]>([]);
  const [userMemberships, setUserMemberships] = useState<StudyGroupMember[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStudyGroups = useCallback(async (filters?: Partial<CommunitySearchFilters>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      if (filters?.study_group_privacy) params.append('privacy_level', filters.study_group_privacy);
      
      const response = await fetch(`${API_BASE}/community/study-groups?${params}`);
      if (!response.ok) throw new Error('Failed to fetch study groups');
      
      const data = await response.json();
      setStudyGroups(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createStudyGroup = useCallback(async (groupData: StudyGroupFormData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/study-groups`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(groupData),
      });
      
      if (!response.ok) throw new Error('Failed to create study group');
      
      const data = await response.json();
      setStudyGroups(prev => [...prev, data]);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const joinStudyGroup = useCallback(async (groupId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/study-groups/${groupId}/join`, {
        method: 'POST',
      });
      
      if (!response.ok) throw new Error('Failed to join study group');
      
      const data = await response.json();
      // Refresh study groups to update member count
      await fetchStudyGroups();
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [fetchStudyGroups]);

  const fetchUserMemberships = useCallback(async (userId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/study-groups/memberships?user_id=${userId}`);
      if (!response.ok) throw new Error('Failed to fetch user memberships');
      
      const data = await response.json();
      setUserMemberships(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    studyGroups,
    userMemberships,
    isLoading,
    error,
    fetchStudyGroups,
    createStudyGroup,
    joinStudyGroup,
    fetchUserMemberships,
  };
}

// Study Sessions Hook
export function useStudySessions() {
  const [sessions, setSessions] = useState<StudySession[]>([]);
  const [attendances, setAttendances] = useState<StudySessionAttendance[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStudySessions = useCallback(async (groupId?: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const params = groupId ? `?group_id=${groupId}` : '';
      const response = await fetch(`${API_BASE}/community/study-sessions${params}`);
      if (!response.ok) throw new Error('Failed to fetch study sessions');
      
      const data = await response.json();
      setSessions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createStudySession = useCallback(async (sessionData: Partial<StudySession>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/study-sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sessionData),
      });
      
      if (!response.ok) throw new Error('Failed to create study session');
      
      const data = await response.json();
      setSessions(prev => [...prev, data]);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const recordAttendance = useCallback(async (sessionId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/study-sessions/${sessionId}/attendance`, {
        method: 'POST',
      });
      
      if (!response.ok) throw new Error('Failed to record attendance');
      
      const data = await response.json();
      // Refresh sessions to update attendance count
      await fetchStudySessions();
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [fetchStudySessions]);

  return {
    sessions,
    attendances,
    isLoading,
    error,
    fetchStudySessions,
    createStudySession,
    recordAttendance,
  };
}

// Office Hours Hook
export function useOfficeHours() {
  const [officeHours, setOfficeHours] = useState<OfficeHour[]>([]);
  const [registrations, setRegistrations] = useState<OfficeHourRegistration[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchOfficeHours = useCallback(async (upcomingOnly: boolean = true) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      params.append('upcoming_only', upcomingOnly.toString());
      
      const response = await fetch(`${API_BASE}/community/office-hours?${params}`);
      if (!response.ok) throw new Error('Failed to fetch office hours');
      
      const data = await response.json();
      setOfficeHours(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createOfficeHour = useCallback(async (hourData: OfficeHourFormData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/office-hours`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(hourData),
      });
      
      if (!response.ok) throw new Error('Failed to create office hour');
      
      const data = await response.json();
      setOfficeHours(prev => [...prev, data]);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const registerForOfficeHour = useCallback(async (hourId: number, topics?: string[]) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/office-hours/${hourId}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          office_hour_id: hourId,
          topics_of_interest: topics ? JSON.stringify(topics) : undefined
        }),
      });
      
      if (!response.ok) throw new Error('Failed to register for office hour');
      
      const data = await response.json();
      // Refresh office hours to update participant count
      await fetchOfficeHours();
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [fetchOfficeHours]);

  const fetchUserRegistrations = useCallback(async (userId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/office-hours/registrations?user_id=${userId}`);
      if (!response.ok) throw new Error('Failed to fetch user registrations');
      
      const data = await response.json();
      setRegistrations(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    officeHours,
    registrations,
    isLoading,
    error,
    fetchOfficeHours,
    createOfficeHour,
    registerForOfficeHour,
    fetchUserRegistrations,
  };
}

// Alumni Network Hook
export function useAlumniNetwork() {
  const [alumniProfiles, setAlumniProfiles] = useState<AlumniProfile[]>([]);
  const [userProfile, setUserProfile] = useState<AlumniProfile | null>(null);
  const [connections, setConnections] = useState<AlumniConnection[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const searchAlumni = useCallback(async (filters?: Partial<CommunitySearchFilters>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      if (filters?.alumni_expertise) {
        params.append('expertise_areas', JSON.stringify(filters.alumni_expertise));
      }
      if (filters?.availability_mentoring !== undefined) {
        params.append('availability_mentoring', filters.availability_mentoring.toString());
      }
      
      const response = await fetch(`${API_BASE}/community/alumni/search?${params}`);
      if (!response.ok) throw new Error('Failed to search alumni');
      
      const data = await response.json();
      setAlumniProfiles(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createAlumniProfile = useCallback(async (profileData: AlumniProfileFormData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/alumni-profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileData),
      });
      
      if (!response.ok) throw new Error('Failed to create alumni profile');
      
      const data = await response.json();
      setUserProfile(data);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateAlumniProfile = useCallback(async (profileId: number, updateData: Partial<AlumniProfileFormData>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/alumni-profile/${profileId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData),
      });
      
      if (!response.ok) throw new Error('Failed to update alumni profile');
      
      const data = await response.json();
      setUserProfile(data);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const connectWithAlumni = useCallback(async (profileId: number, connectionType: string = 'network', message?: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/alumni/${profileId}/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ connection_type: connectionType, message }),
      });
      
      if (!response.ok) throw new Error('Failed to connect with alumni');
      
      const data = await response.json();
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchUserProfile = useCallback(async (userId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/alumni-profile/user/${userId}`);
      if (!response.ok) throw new Error('Failed to fetch user profile');
      
      const data = await response.json();
      setUserProfile(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    alumniProfiles,
    userProfile,
    connections,
    isLoading,
    error,
    searchAlumni,
    createAlumniProfile,
    updateAlumniProfile,
    connectWithAlumni,
    fetchUserProfile,
  };
}

// Job Opportunities Hook
export function useJobOpportunities() {
  const [jobs, setJobs] = useState<JobOpportunity[]>([]);
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchJobs = useCallback(async (filters?: Partial<CommunitySearchFilters>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      if (filters?.job_employment_type) params.append('employment_type', filters.job_employment_type);
      if (filters?.is_remote !== undefined) params.append('is_remote', filters.is_remote.toString());
      if (filters?.location) params.append('location', filters.location);
      
      const response = await fetch(`${API_BASE}/community/jobs?${params}`);
      if (!response.ok) throw new Error('Failed to fetch job opportunities');
      
      const data = await response.json();
      setJobs(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createJob = useCallback(async (jobData: JobOpportunityFormData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jobData),
      });
      
      if (!response.ok) throw new Error('Failed to create job opportunity');
      
      const data = await response.json();
      setJobs(prev => [...prev, data]);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const applyForJob = useCallback(async (jobId: number, applicationData: Partial<JobApplication>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/jobs/${jobId}/apply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...applicationData, job_opportunity_id: jobId }),
      });
      
      if (!response.ok) throw new Error('Failed to apply for job');
      
      const data = await response.json();
      setApplications(prev => [...prev, data]);
      // Refresh jobs to update application count
      await fetchJobs();
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [fetchJobs]);

  const fetchUserApplications = useCallback(async (userId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/jobs/applications?user_id=${userId}`);
      if (!response.ok) throw new Error('Failed to fetch user applications');
      
      const data = await response.json();
      setApplications(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    jobs,
    applications,
    isLoading,
    error,
    fetchJobs,
    createJob,
    applyForJob,
    fetchUserApplications,
  };
}

// Community Analytics Hook
export function useCommunityAnalytics() {
  const [dashboard, setDashboard] = useState<CommunityDashboard | null>(null);
  const [engagementMetrics, setEngagementMetrics] = useState<CommunityEngagementMetrics | null>(null);
  const [eventAnalytics, setEventAnalytics] = useState<EventAnalytics | null>(null);
  const [studyGroupAnalytics, setStudyGroupAnalytics] = useState<StudyGroupAnalytics | null>(null);
  const [alumniAnalytics, setAlumniAnalytics] = useState<AlumniNetworkAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/dashboard`);
      if (!response.ok) throw new Error('Failed to fetch community dashboard');
      
      const data = await response.json();
      setDashboard(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchEngagementMetrics = useCallback(async (days: number = 30) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/engagement/metrics?days=${days}`);
      if (!response.ok) throw new Error('Failed to fetch engagement metrics');
      
      const data = await response.json();
      setEngagementMetrics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchEventAnalytics = useCallback(async (eventId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/events/${eventId}/analytics`);
      if (!response.ok) throw new Error('Failed to fetch event analytics');
      
      const data = await response.json();
      setEventAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchStudyGroupAnalytics = useCallback(async (groupId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/study-groups/${groupId}/analytics`);
      if (!response.ok) throw new Error('Failed to fetch study group analytics');
      
      const data = await response.json();
      setStudyGroupAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchAlumniAnalytics = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/alumni/analytics`);
      if (!response.ok) throw new Error('Failed to fetch alumni analytics');
      
      const data = await response.json();
      setAlumniAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    dashboard,
    engagementMetrics,
    eventAnalytics,
    studyGroupAnalytics,
    alumniAnalytics,
    isLoading,
    error,
    fetchDashboard,
    fetchEngagementMetrics,
    fetchEventAnalytics,
    fetchStudyGroupAnalytics,
    fetchAlumniAnalytics,
  };
}

// Community Notifications Hook
export function useCommunityNotifications() {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchNotifications = useCallback(async (userId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/notifications?user_id=${userId}`);
      if (!response.ok) throw new Error('Failed to fetch notifications');
      
      const data = await response.json();
      setNotifications(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const markAsRead = useCallback(async (notificationId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/notifications/${notificationId}/read`, {
        method: 'POST',
      });
      
      if (!response.ok) throw new Error('Failed to mark notification as read');
      
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const markAllAsRead = useCallback(async (userId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/community/notifications/mark-all-read?user_id=${userId}`, {
        method: 'POST',
      });
      
      if (!response.ok) throw new Error('Failed to mark all notifications as read');
      
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    notifications,
    isLoading,
    error,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
  };
}