'use client';

import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';

interface Course {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  instructor: string;
  category: string;
  duration: string;
  lessons: number;
  enrolledCount: number;
  rating: number;
  progress?: number;
  completedLessons?: number;
  totalLessons?: number;
}

interface CourseListProps {
  courses: Course[];
  variant?: 'grid' | 'list';
  showProgress?: boolean;
}

export function CourseList({ courses, variant = 'grid', showProgress = false }: CourseListProps) {
  if (variant === 'list') {
    return (
      <div className="space-y-4">
        {courses.map((course) => (
          <Card key={course.id} className="overflow-hidden hover:shadow-lg transition-shadow">
            <div className="flex flex-col sm:flex-row">
              <div className="w-full sm:w-48 h-32 bg-gray-200 flex-shrink-0">
                {course.thumbnail && (
                  <img
                    src={course.thumbnail}
                    alt={course.title}
                    className="w-full h-full object-cover"
                  />
                )}
              </div>
              <div className="flex-1 p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <Badge variant="outline" className="mb-2">{course.category}</Badge>
                    <h3 className="font-semibold text-gray-900 line-clamp-1">{course.title}</h3>
                    <p className="text-sm text-gray-500 mt-1">{course.instructor}</p>
                    <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                      <span>⏱️ {course.duration}</span>
                      <span>📚 {course.lessons} lessons</span>
                      <span>👥 {course.enrolledCount.toLocaleString()} enrolled</span>
                      <span>⭐ {course.rating.toFixed(1)}</span>
                    </div>
                    {showProgress && course.progress !== undefined && (
                      <div className="mt-3">
                        <div className="flex items-center justify-between text-sm mb-1">
                          <span className="text-gray-600">Progress</span>
                          <span className="font-medium">{course.progress}%</span>
                        </div>
                        <Progress value={course.progress} className="h-2" />
                      </div>
                    )}
                  </div>
                  <div className="mt-4 sm:mt-0 sm:ml-4">
                    <Button asChild size="sm">
                      <Link href={`/courses/${course.id}`}>
                        {course.progress === 100 ? 'Review' : 'Start Learning'}
                      </Link>
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {courses.map((course) => (
        <Card key={course.id} className="overflow-hidden hover:shadow-lg transition-shadow group">
          <div className="w-full h-40 bg-gray-200 relative">
            {course.thumbnail && (
              <img
                src={course.thumbnail}
                alt={course.title}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
            )}
            {course.progress !== undefined && course.progress > 0 && (
              <Badge
                className="absolute top-2 right-2"
                variant={course.progress === 100 ? 'default' : 'secondary'}
              >
                {course.progress === 100 ? 'Completed' : `${course.progress}%`}
              </Badge>
            )}
          </div>
          <CardContent className="p-4">
            <Badge variant="outline" className="mb-2 text-xs">{course.category}</Badge>
            <h3 className="font-semibold text-gray-900 line-clamp-2 mb-1">{course.title}</h3>
            <p className="text-sm text-gray-500 mb-3">{course.instructor}</p>
            <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
              <span>⏱️ {course.duration}</span>
              <span>⭐ {course.rating.toFixed(1)}</span>
            </div>
            {showProgress && course.progress !== undefined && (
              <div className="mb-3">
                <Progress value={course.progress} className="h-2" />
                <p className="text-xs text-gray-500 mt-1">
                  {course.completedLessons || 0}/{course.totalLessons || course.lessons} lessons
                </p>
              </div>
            )}
            <Button variant="outline" className="w-full" size="sm" asChild>
              <Link href={`/courses/${course.id}`}>
                {course.progress === 100 ? 'Review Course' : 'View Course'}
              </Link>
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
