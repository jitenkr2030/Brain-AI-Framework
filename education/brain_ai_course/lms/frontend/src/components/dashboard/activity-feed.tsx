'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface Activity {
  id: string;
  type: 'course_started' | 'course_completed' | 'lesson_completed' | 'certificate_earned' | 'achievement';
  title: string;
  description: string;
  timestamp: string;
  icon?: string;
}

interface ActivityFeedProps {
  activities: Activity[];
  limit?: number;
}

const activityConfig = {
  course_started: {
    icon: '📚',
    color: 'bg-blue-100 text-blue-600',
    badge: 'info',
  },
  course_completed: {
    icon: '✅',
    color: 'bg-green-100 text-green-600',
    badge: 'success',
  },
  lesson_completed: {
    icon: '🎯',
    color: 'bg-purple-100 text-purple-600',
    badge: 'default',
  },
  certificate_earned: {
    icon: '🏆',
    color: 'bg-yellow-100 text-yellow-600',
    badge: 'warning',
  },
  achievement: {
    icon: '⭐',
    color: 'bg-orange-100 text-orange-600',
    badge: 'secondary',
  },
};

export function ActivityFeed({ activities, limit = 10 }: ActivityFeedProps) {
  const displayedActivities = activities.slice(0, limit);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Recent Activity</span>
          <Badge variant="outline">{activities.length} activities</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {displayedActivities.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No recent activity</p>
              <p className="text-sm mt-1">Start learning to see your activity here!</p>
            </div>
          ) : (
            displayedActivities.map((activity) => {
              const config = activityConfig[activity.type];
              return (
                <div
                  key={activity.id}
                  className="flex items-start space-x-4 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${config.color}`}>
                    <span className="text-lg">{config.icon}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900">{activity.title}</p>
                    <p className="text-sm text-gray-500 mt-0.5">{activity.description}</p>
                    <p className="text-xs text-gray-400 mt-1">{formatTimestamp(activity.timestamp)}</p>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </CardContent>
    </Card>
  );
}
