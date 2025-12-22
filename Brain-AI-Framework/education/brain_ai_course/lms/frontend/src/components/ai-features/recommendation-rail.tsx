'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import type { CourseRecommendation } from '@/types/brain-ai';
import { useBrainRecommendations } from '@/hooks/use-brain-ai';

interface RecommendationRailProps {
  userId: string;
  limit?: number;
  title?: string;
  showReasoning?: boolean;
  onCourseClick?: (courseId: string) => void;
}

export function RecommendationRail({
  userId,
  limit = 5,
  title = 'Recommended for You',
  showReasoning = true,
  onCourseClick,
}: RecommendationRailProps) {
  const { recommendations, isLoading, error, refresh, filters, setFilters } =
    useBrainRecommendations({
      userId,
      limit,
      enabled: !!userId,
    });

  const [isExpanded, setIsExpanded] = useState(false);
  const displayedCourses = isExpanded
    ? recommendations
    : recommendations.slice(0, 3);

  if (error) {
    return (
      <div className="p-4 border border-red-200 rounded-lg bg-red-50">
        <p className="text-red-600 text-sm">Unable to load recommendations</p>
        <Button variant="outline" size="sm" onClick={refresh} className="mt-2">
          Try Again
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-xl">✨</span>
          <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
        </div>
        {recommendations.length > 3 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? 'Show Less' : `Show All (${recommendations.length})`}
          </Button>
        )}
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-48 w-full rounded-lg" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {displayedCourses.map((course) => (
            <CourseRecommendationCard
              key={course.course_id}
              course={course}
              showReasoning={showReasoning}
              onClick={() => onCourseClick?.(course.course_id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

interface CourseRecommendationCardProps {
  course: CourseRecommendation;
  showReasoning?: boolean;
  onClick?: () => void;
}

function CourseRecommendationCard({
  course,
  showReasoning = true,
  onClick,
}: CourseRecommendationCardProps) {
  const getMatchColor = (score: number) => {
    if (score >= 90) return 'bg-green-100 text-green-700';
    if (score >= 75) return 'bg-blue-100 text-blue-700';
    if (score >= 60) return 'bg-yellow-100 text-yellow-700';
    return 'bg-gray-100 text-gray-700';
  };

  return (
    <Card
      className="overflow-hidden hover:shadow-lg transition-all cursor-pointer group"
      onClick={onClick}
    >
      <div className="relative w-full h-32 bg-gradient-to-br from-indigo-500 to-purple-600">
        <div className="absolute top-2 right-2">
          <Badge className={`${getMatchColor(course.match_score)} font-mono text-sm`}>
            {course.match_score}% Match
          </Badge>
        </div>
        <div className="absolute bottom-2 left-2">
          <span className="text-white/80 text-xs">{course.category || 'Course'}</span>
        </div>
      </div>

      <CardContent className="p-4">
        <h3 className="font-semibold text-gray-900 line-clamp-2 group-hover:text-blue-600 transition-colors">
          {course.title}
        </h3>
        <p className="text-sm text-gray-500 mt-1">{course.instructor}</p>

        {showReasoning && course.reasoning && (
          <div className="mt-3 p-2 bg-gray-50 rounded text-xs text-gray-600">
            <span className="font-medium">Why:</span> {course.reasoning}
          </div>
        )}

        <div className="flex items-center justify-between mt-3">
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            {course.duration && <span>⏱️ {course.duration}</span>}
            {course.rating && (
              <span className="flex items-center">
                ⭐ {course.rating.toFixed(1)}
              </span>
            )}
          </div>
          <Button size="sm" variant="outline">
            View Course
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// Skeleton component for loading states
export function RecommendationRailSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2">
        <span className="text-xl">✨</span>
        <Skeleton className="h-6 w-48" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="space-y-3">
            <Skeleton className="h-32 w-full rounded-lg" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
            <Skeleton className="h-8 w-full" />
          </div>
        ))}
      </div>
    </div>
  );
}
