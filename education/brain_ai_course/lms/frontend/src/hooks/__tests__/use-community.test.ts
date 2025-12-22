/**
 * Unit Tests for use-community.ts
 * Brain AI LMS - Community Hook Tests
 */

import { renderHook, waitFor } from '@testing-library/react';
import { useEvents, useStudyGroups, useStudySessions, useOfficeHours, useAlumniNetwork, useJobOpportunities, useCommunityAnalytics, useCommunityNotifications } from '../use-community';

// Mock fetch globally
global.fetch = jest.fn();

describe('useEvents', () => {
  const mockEvents = [
    {
      id: 1,
      title: 'Weekly Study Session',
      eventType: 'study_group',
      startDate: '2024-02-01T18:00:00Z',
      endDate: '2024-02-01T20:00:00Z',
      location: 'Online',
      description: 'Join us for our weekly study session',
      maxAttendees: 50,
      currentAttendees: 25,
    },
    {
      id: 2,
      title: 'AI Workshop',
      eventType: 'workshop',
      startDate: '2024-02-15T10:00:00Z',
      endDate: '2024-02-15T16:00:00Z',
      location: 'Tech Hub',
      description: 'Hands-on workshop on neural networks',
      maxAttendees: 30,
      currentAttendees: 28,
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockEvents,
    });
  });

  it('should initialize with empty events', () => {
    const { result } = renderHook(() => useEvents());

    expect(result.current.events).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should fetch upcoming events', async () => {
    const { result } = renderHook(() => useEvents());

    result.current.fetchEvents();

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.events).toEqual(mockEvents);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('upcoming_only=true'),
      expect.any(Object)
    );
  });

  it('should fetch events with filters', async () => {
    const { result } = renderHook(() => useEvents());

    result.current.fetchEvents({
      eventType: 'workshop',
      dateRange: { start: '2024-02-01', end: '2024-02-28' },
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('event_type=workshop'),
        expect.any(Object)
      );
    });
  });

  it('should create new event', async () => {
    const newEvent = {
      title: 'New Workshop',
      eventType: 'workshop',
      startDate: '2024-03-01T10:00:00Z',
      endDate: '2024-03-01T12:00:00Z',
      location: 'Online',
      description: 'New workshop description',
    };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 3, ...newEvent }),
    });

    const { result } = renderHook(() => useEvents());
    await result.current.fetchEvents();

    const created = await result.current.createEvent(newEvent);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/community/events'),
      expect.objectContaining({ method: 'POST' })
    );
    expect(created.id).toBe(3);
  });

  it('should update existing event', async () => {
    const updateData = { title: 'Updated Workshop', maxAttendees: 50 };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 2, ...updateData }),
    });

    const { result } = renderHook(() => useEvents());
    await result.current.fetchEvents();

    await result.current.updateEvent(2, updateData);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/community/events/2'),
      expect.objectContaining({ method: 'PUT' })
    );
  });

  it('should register for event', async () => {
    const mockRegistration = { id: 101, eventId: 1, userId: 123, registeredAt: '2024-01-20' };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockRegistration,
    });

    const { result } = renderHook(() => useEvents());
    await result.current.fetchEvents();

    const registration = await result.current.registerForEvent(1);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/community/events/1/register'),
      expect.objectContaining({ method: 'POST' })
    );
    expect(registration.eventId).toBe(1);
  });

  it('should confirm attendance', async () => {
    const mockConfirmation = { success: true, message: 'Attendance confirmed' };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockConfirmation,
    });

    const { result } = renderHook(() => useEvents());
    await result.current.fetchEvents();

    const confirmation = await result.current.confirmAttendance(1);

    expect(confirmation.success).toBe(true);
  });

  it('should handle fetch error', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 500,
    });

    const { result } = renderHook(() => useEvents());

    result.current.fetchEvents();

    await waitFor(() => {
      expect(result.current.error).toBe('Failed to fetch events');
    });
  });
});

describe('useStudyGroups', () => {
  const mockStudyGroups = [
    {
      id: 1,
      name: 'Python Beginners',
      description: 'For those just starting with Python',
      privacyLevel: 'public',
      maxMembers: 20,
      currentMembers: 12,
      courseId: 101,
    },
    {
      id: 2,
      name: 'Machine Learning Advanced',
      description: 'Deep dive into ML algorithms',
      privacyLevel: 'private',
      maxMembers: 10,
      currentMembers: 8,
      courseId: 102,
    },
  ];

  const mockMemberships = [
    { id: 1, groupId: 1, userId: 123, joinedAt: '2024-01-01' },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockStudyGroups,
    });
  });

  it('should fetch study groups', async () => {
    const { result } = renderHook(() => useStudyGroups());

    result.current.fetchStudyGroups();

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.studyGroups).toEqual(mockStudyGroups);
  });

  it('should filter study groups by privacy', async () => {
    const { result } = renderHook(() => useStudyGroups());

    result.current.fetchStudyGroups({ studyGroupPrivacy: 'public' });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('privacy_level=public'),
        expect.any(Object)
      );
    });
  });

  it('should create study group', async () => {
    const newGroup = {
      name: 'Data Science Study Group',
      description: 'Learning data science together',
      privacyLevel: 'public',
      maxMembers: 25,
      courseId: 103,
    };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 3, ...newGroup }),
    });

    const { result } = renderHook(() => useStudyGroups());
    await result.current.fetchStudyGroups();

    const created = await result.current.createStudyGroup(newGroup);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/community/study-groups'),
      expect.objectContaining({ method: 'POST' })
    );
    expect(created.id).toBe(3);
  });

  it('should join study group', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 2, groupId: 1, userId: 123 }),
    });

    const { result } = renderHook(() => useStudyGroups());
    await result.current.fetchStudyGroups();

    await result.current.joinStudyGroup(1);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/community/study-groups/1/join'),
      expect.objectContaining({ method: 'POST' })
    );
  });

  it('should fetch user memberships', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockMemberships,
    });

    const { result } = renderHook(() => useStudyGroups());

    result.current.fetchUserMemberships(123);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('user_id=123'),
        expect.any(Object)
      );
    });
  });
});

describe('useStudySessions', () => {
  const mockSessions = [
    {
      id: 1,
      groupId: 1,
      title: 'Review Session - Chapter 5',
      startTime: '2024-02-01T19:00:00Z',
      endTime: '2024-02-01T21:00:00Z',
      topic: 'Neural Networks',
      attendanceCount: 8,
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockSessions,
    });
  });

  it('should fetch study sessions', async () => {
    const { result } = renderHook(() => useStudySessions());

    result.current.fetchStudySessions();

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.sessions).toEqual(mockSessions);
  });

  it('should fetch sessions for specific group', async () => {
    const { result } = renderHook(() => useStudySessions());

    result.current.fetchStudySessions(1);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('group_id=1'),
        expect.any(Object)
      );
    });
  });

  it('should create study session', async () => {
    const newSession = {
      groupId: 1,
      title: 'Practice Session',
      startTime: '2024-02-05T18:00:00Z',
      endTime: '2024-02-05T20:00:00Z',
      topic: 'Python Basics',
    };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 2, ...newSession }),
    });

    const { result } = renderHook(() => useStudySessions());
    await result.current.fetchStudySessions();

    const created = await result.current.createStudySession(newSession);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/community/study-sessions'),
      expect.objectContaining({ method: 'POST' })
    );
    expect(created.id).toBe(2);
  });

  it('should record attendance', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ success: true, sessionId: 1 }),
    });

    const { result } = renderHook(() => useStudySessions());
    await result.current.fetchStudySessions();

    await result.current.recordAttendance(1);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/community/study-sessions/1/attendance'),
      expect.objectContaining({ method: 'POST' })
    );
  });
});

describe('useOfficeHours', () => {
  const mockOfficeHours = [
    {
      id: 1,
      instructorId: 456,
      instructorName: 'Dr. Smith',
      title: 'AI Office Hours',
      startTime: '2024-02-02T14:00:00Z',
      endTime: '2024-02-02T16:00:00Z',
      maxParticipants: 10,
      currentParticipants: 5,
      topics: ['Neural Networks', 'Deep Learning'],
    },
  ];

  const mockRegistrations = [
    { id: 1, officeHourId: 1, userId: 123, registeredAt: '2024-01-25' },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockOfficeHours,
    });
  });

  it('should fetch office hours', async () => {
    const { result } = renderHook(() => useOfficeHours());

    result.current.fetchOfficeHours();

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.officeHours).toEqual(mockOfficeHours);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('upcoming_only=true'),
      expect.any(Object)
    );
  });

  it('should create office hour', async () => {
    const newHour = {
      instructorId: 456,
      title: 'ML Office Hours',
      startTime: '2024-02-09T15:00:00Z',
      endTime: '2024-02-09T17:00:00Z',
      maxParticipants: 15,
    };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 2, ...newHour }),
    });

    const { result } = renderHook(() => useOfficeHours());
    await result.current.fetchOfficeHours();

    const created = await result.current.createOfficeHour(newHour);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/community/office-hours'),
      expect.objectContaining({ method: 'POST' })
    );
    expect(created.id).toBe(2);
  });

  it('should register for office hour', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 2, officeHourId: 1, userId: 123 }),
    });

    const { result } = renderHook(() => useOfficeHours());
    await result.current.fetchOfficeHours();

    await result.current.registerForOfficeHour(1, ['Neural Networks', 'CNN']);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/community/office-hours/1/register'),
      expect.objectContaining({ method: 'POST' })
    );
  });

  it('should fetch user registrations', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockRegistrations,
    });

    const { result } = renderHook(() => useOfficeHours());

    result.current.fetchUserRegistrations(123);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('user_id=123'),
        expect.any(Object)
      );
    });
  });
});

describe('useAlumniNetwork', () => {
  const mockAlumniProfiles = [
    {
      id: 1,
      userId: 789,
      name: 'Jane Doe',
      graduationYear: 2020,
      currentCompany: 'Google',
      currentRole: 'Senior ML Engineer',
      expertiseAreas: ['Machine Learning', 'NLP', 'Computer Vision'],
      availabilityForMentoring: true,
      bio: 'Passionate about AI and education',
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockAlumniProfiles,
    });
  });

  it('should search alumni', async () => {
    const { result } = renderHook(() => useAlumniNetwork());

    result.current.searchAlumni({ alumniExpertise: ['Machine Learning'] });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.alumniProfiles).toEqual(mockAlumniProfiles);
  });

  it('should filter by mentoring availability', async () => {
    const { result } = renderHook(() => useAlumniNetwork());

    result.current.searchAlumni({ availabilityMentoring: true });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('availability_mentoring=true'),
        expect.any(Object)
      );
    });
  });

  it('should create alumni profile', async () => {
    const newProfile = {
      graduationYear: 2023,
      currentCompany: 'Startup Inc',
      currentRole: 'Data Scientist',
      expertiseAreas: ['Data Science', 'Analytics'],
      availabilityForMentoring: true,
      bio: 'Recent graduate eager to help',
    };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 2, ...newProfile }),
    });

    const { result } = renderHook(() => useAlumniNetwork());

    const created = await result.current.createAlumniProfile(newProfile);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/community/alumni-profile'),
      expect.objectContaining({ method: 'POST' })
    );
    expect(created.id).toBe(2);
  });

  it('should connect with alumni', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ success: true, connectionId: 101 }),
    });

    const { result } = renderHook(() => useAlumniNetwork());

    const connection = await result.current.connectWithAlumni(1, 'mentoring', 'Looking for guidance');

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/community/alumni/1/connect'),
      expect.objectContaining({ method: 'POST' })
    );
    expect(connection.success).toBe(true);
  });

  it('should fetch user profile', async () => {
    const mockProfile = { id: 1, userId: 123, name: 'John Smith' };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockProfile,
    });

    const { result } = renderHook(() => useAlumniNetwork());

    result.current.fetchUserProfile(123);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/community/alumni-profile/user/123'),
        expect.any(Object)
      );
    });
  });
});

describe('useJobOpportunities', () => {
  const mockJobs = [
    {
      id: 1,
      title: 'Machine Learning Engineer',
      company: 'Tech Corp',
      location: 'San Francisco, CA',
      employmentType: 'full_time',
      isRemote: true,
      salaryRange: '$120,000 - $180,000',
      description: 'Build ML models at scale',
      requiredSkills: ['Python', 'TensorFlow', 'AWS'],
      postedAt: '2024-01-15',
      applicationCount: 45,
    },
  ];

  const mockApplications = [
    { id: 1, jobId: 1, userId: 123, status: 'pending', appliedAt: '2024-01-20' },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockJobs,
    });
  });

  it('should fetch job opportunities', async () => {
    const { result } = renderHook(() => useJobOpportunities());

    result.current.fetchJobs();

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.jobs).toEqual(mockJobs);
  });

  it('should filter jobs by employment type', async () => {
    const { result } = renderHook(() => useJobOpportunities());

    result.current.fetchJobs({ jobEmploymentType: 'full_time' });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('employment_type=full_time'),
        expect.any(Object)
      );
    });
  });

  it('should filter jobs by remote status', async () => {
    const { result } = renderHook(() => useJobOpportunities());

    result.current.fetchJobs({ isRemote: true });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('is_remote=true'),
        expect.any(Object)
      );
    });
  });

  it('should create job posting', async () => {
    const newJob = {
      title: 'Data Scientist',
      company: 'Data Inc',
      location: 'New York, NY',
      employmentType: 'full_time',
      isRemote: false,
      salaryRange: '$100,000 - $150,000',
      description: 'Analyze data and build models',
    };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 2, ...newJob }),
    });

    const { result } = renderHook(() => useJobOpportunities());

    const created = await result.current.createJob(newJob);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/community/jobs'),
      expect.objectContaining({ method: 'POST' })
    );
    expect(created.id).toBe(2);
  });

  it('should apply for job', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 2, jobId: 1, userId: 123, status: 'pending' }),
    });

    const { result } = renderHook(() => useJobOpportunities());
    await result.current.fetchJobs();

    const application = await result.current.applyForJob(1, { coverLetter: 'I am excited to apply...' });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/community/jobs/1/apply'),
      expect.objectContaining({ method: 'POST' })
    );
    expect(application.jobId).toBe(1);
  });

  it('should fetch user applications', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockApplications,
    });

    const { result } = renderHook(() => useJobOpportunities());

    result.current.fetchUserApplications(123);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('user_id=123'),
        expect.any(Object)
      );
    });
  });
});

describe('useCommunityAnalytics', () => {
  const mockDashboard = {
    totalMembers: 1500,
    activeMembers: 850,
    totalGroups: 45,
    totalEvents: 120,
    engagementRate: 0.68,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockDashboard,
    });
  });

  it('should fetch community dashboard', async () => {
    const { result } = renderHook(() => useCommunityAnalytics());

    result.current.fetchDashboard();

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.dashboard).toEqual(mockDashboard);
  });

  it('should fetch engagement metrics', async () => {
    const mockMetrics = {
      dailyActiveUsers: [120, 135, 142, 128, 156],
      weeklyRetention: 0.75,
      monthlyRetention: 0.62,
    };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockMetrics,
    });

    const { result } = renderHook(() => useCommunityAnalytics());

    result.current.fetchEngagementMetrics(30);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('days=30'),
        expect.any(Object)
      );
    });
  });

  it('should fetch event analytics', async () => {
    const mockEventAnalytics = {
      eventId: 1,
      totalRegistrations: 50,
      actualAttendees: 42,
      averageRating: 4.5,
      feedbackCount: 35,
    };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockEventAnalytics,
    });

    const { result } = renderHook(() => useCommunityAnalytics());

    result.current.fetchEventAnalytics(1);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/community/events/1/analytics'),
        expect.any(Object)
      );
    });
  });

  it('should fetch study group analytics', async () => {
    const mockGroupAnalytics = {
      groupId: 1,
      totalMembers: 20,
      activeMembers: 15,
      meetingsHeld: 12,
      averageAttendance: 0.72,
    };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockGroupAnalytics,
    });

    const { result } = renderHook(() => useCommunityAnalytics());

    result.current.fetchStudyGroupAnalytics(1);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/community/study-groups/1/analytics'),
        expect.any(Object)
      );
    });
  });

  it('should fetch alumni analytics', async () => {
    const mockAlumniAnalytics = {
      totalAlumni: 500,
      employedAlumni: 450,
      averageSalary: 95000,
      mentoringParticipation: 0.35,
    };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockAlumniAnalytics,
    });

    const { result } = renderHook(() => useCommunityAnalytics());

    result.current.fetchAlumniAnalytics();

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/community/alumni/analytics'),
        expect.any(Object)
      );
    });
  });
});

describe('useCommunityNotifications', () => {
  const mockNotifications = [
    {
      id: 1,
      type: 'event_reminder',
      title: 'Event Starting Soon',
      message: 'AI Workshop starts in 30 minutes',
      isRead: false,
      createdAt: '2024-02-01T09:30:00Z',
    },
    {
      id: 2,
      type: 'group_update',
      title: 'New Member Joined',
      message: 'John Doe joined Python Beginners',
      isRead: true,
      createdAt: '2024-02-01T08:00:00Z',
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockNotifications,
    });
  });

  it('should fetch notifications for user', async () => {
    const { result } = renderHook(() => useCommunityNotifications());

    result.current.fetchNotifications(123);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.notifications).toEqual(mockNotifications);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('user_id=123'),
      expect.any(Object)
    );
  });

  it('should mark notification as read', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({}),
    });

    const { result } = renderHook(() => useCommunityNotifications());
    await result.current.fetchNotifications(123);

    await result.current.markAsRead(1);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/community/notifications/1/read'),
      expect.objectContaining({ method: 'POST' })
    );
    expect(result.current.notifications[0].isRead).toBe(true);
  });

  it('should mark all notifications as read', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({}),
    });

    const { result } = renderHook(() => useCommunityNotifications());
    await result.current.fetchNotifications(123);

    await result.current.markAllAsRead(123);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/community/notifications/mark-all-read'),
      expect.objectContaining({ method: 'POST' })
    );
    expect(result.current.notifications.every(n => n.isRead)).toBe(true);
  });
});
