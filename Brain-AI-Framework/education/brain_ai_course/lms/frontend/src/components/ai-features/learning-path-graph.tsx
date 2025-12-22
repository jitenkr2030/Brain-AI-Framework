'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { useLearningPath } from '@/hooks/use-brain-ai';
import type { LearningPathModule } from '@/types/brain-ai';

interface LearningPathGraphProps {
  userId: string;
  targetGoal: string;
  currentSkills?: { [skill: string]: number };
  onModuleClick?: (moduleId: string) => void;
  editable?: boolean;
}

export function LearningPathGraph({
  userId,
  targetGoal,
  currentSkills = {},
  onModuleClick,
  editable = false,
}: LearningPathGraphProps) {
  const { learningPath, isLoading, error, generateNewPath, refresh } =
    useLearningPath({
      userId,
      targetGoal,
      currentSkills,
      enabled: !!userId,
    });

  const [selectedGoal, setSelectedGoal] = useState(targetGoal);

  const goals = [
    'Become a Data Scientist',
    'Master Machine Learning',
    'Full Stack Developer',
    'DevOps Engineer',
    'AI Research Scientist',
  ];

  if (error) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center">
            <p className="text-red-600">Unable to load learning path</p>
            <Button variant="outline" onClick={refresh} className="mt-2">
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isLoading && !learningPath) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Goal Selector */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center space-x-2">
            <span>🎯</span>
            <span>Your Learning Goal</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {editable ? (
            <div className="space-y-3">
              <select
                value={selectedGoal}
                onChange={(e) => setSelectedGoal(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {goals.map((goal) => (
                  <option key={goal} value={goal}>
                    {goal}
                  </option>
                ))}
              </select>
              <Button
                onClick={() => generateNewPath(selectedGoal)}
                disabled={isLoading}
                className="w-full"
              >
                {isLoading ? 'Generating...' : 'Generate New Path'}
              </Button>
            </div>
          ) : (
            <div className="flex items-center justify-between p-3 bg-indigo-50 rounded-lg">
              <span className="font-medium text-indigo-900">{targetGoal}</span>
              <Badge variant="outline">AI Generated</Badge>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Learning Path Timeline */}
      {learningPath && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span>📚</span>
                <span>Your Personalized Path</span>
              </div>
              <div className="flex items-center space-x-2 text-sm font-normal">
                <span className="text-gray-500">
                  {learningPath.total_modules} modules
                </span>
                <span className="text-gray-300">•</span>
                <span className="text-gray-500">
                  {learningPath.estimated_duration}
                </span>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative">
              {/* Vertical Line */}
              <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200" />

              {/* Module Steps */}
              <div className="space-y-4">
                {learningPath.modules.map((module, index) => (
                  <LearningPathStep
                    key={module.module_id}
                    module={module}
                    index={index}
                    isLast={index === learningPath.modules.length - 1}
                    onClick={() => onModuleClick?.(module.module_id)}
                  />
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* AI Insights */}
      {learningPath && (
        <Card className="bg-gradient-to-r from-indigo-50 to-purple-50 border-indigo-200">
          <CardHeader>
            <CardTitle className="text-lg flex items-center space-x-2">
              <span>💡</span>
              <span>AI Insights</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <span className="text-xl">⏱️</span>
                <div>
                  <p className="font-medium text-gray-900">Estimated Time</p>
                  <p className="text-sm text-gray-600">
                    Based on your learning pace, you can complete this path in{' '}
                    {learningPath.estimated_duration}
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-xl">🎯</span>
                <div>
                  <p className="font-medium text-gray-900">Prerequisites</p>
                  <p className="text-sm text-gray-600">
                    Modules are ordered to build on each other. Complete them in
                    order for best results.
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-xl">📈</span>
                <div>
                  <p className="font-medium text-gray-900">Progress Tracking</p>
                  <p className="text-sm text-gray-600">
                    AI will adapt this path based on your performance and time
                    spent on each module.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

interface LearningPathStepProps {
  module: LearningPathModule;
  index: number;
  isLast: boolean;
  onClick?: () => void;
}

function LearningPathStep({
  module,
  index,
  isLast,
  onClick,
}: LearningPathStepProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'in_progress':
        return 'bg-blue-500';
      default:
        return 'bg-gray-300';
    }
  };

  return (
    <div className="relative flex items-start space-x-4">
      {/* Timeline Node */}
      <div className="relative z-10 flex-shrink-0">
        <div
          className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-sm ${getStatusColor(
            module.status
          )}`}
        >
          {module.status === 'completed' ? (
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          ) : module.status === 'in_progress' ? (
            <span>{module.order}</span>
          ) : (
            <span>{module.order}</span>
          )}
        </div>
      </div>

      {/* Content Card */}
      <div className="flex-1">
        <Card
          className={`cursor-pointer transition-all ${
            isExpanded ? 'ring-2 ring-indigo-500' : 'hover:shadow-md'
          }`}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h4 className="font-semibold text-gray-900">{module.title}</h4>
                  <Badge variant="outline" className="text-xs">
                    {module.duration}
                  </Badge>
                </div>
                <p className="text-sm text-gray-500 mt-1">{module.rationale}</p>

                {/* Expanded Content */}
                {isExpanded && (
                  <div className="mt-4 space-y-3">
                    {module.prerequisites.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase">
                          Prerequisites
                        </p>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {module.prerequisites.map((prereq) => (
                            <Badge key={prereq} variant="secondary">
                              {prereq}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex space-x-2 pt-2">
                      <Button
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onClick?.();
                        }}
                      >
                        {module.status === 'completed'
                          ? 'Review Module'
                          : module.status === 'in_progress'
                          ? 'Continue'
                          : 'Start Module'}
                      </Button>
                      <Button size="sm" variant="outline">
                        More Info
                      </Button>
                    </div>
                  </div>
                )}
              </div>

              {/* Expand/Collapse Indicator */}
              <div className="ml-4 flex-shrink-0">
                <svg
                  className={`w-5 h-5 text-gray-400 transition-transform ${
                    isExpanded ? 'rotate-180' : ''
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Compact version for dashboard sidebar
export function CompactLearningPath({
  userId,
  targetGoal,
}: {
  userId: string;
  targetGoal: string;
}) {
  const { learningPath, isLoading } = useLearningPath({
    userId,
    targetGoal,
    enabled: !!userId,
  });

  if (isLoading || !learningPath) {
    return <Skeleton className="h-48 w-full" />;
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center space-x-2">
          <span>🎯</span>
          <span>Current Path</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="font-medium text-sm">{targetGoal}</p>
        <div className="mt-3 space-y-2">
          {learningPath.modules.slice(0, 3).map((module, index) => (
            <div key={module.module_id} className="flex items-center space-x-2">
              <div className="w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center text-xs font-medium text-indigo-600">
                {index + 1}
              </div>
              <span className="text-xs text-gray-600 line-clamp-1">
                {module.title}
              </span>
            </div>
          ))}
        </div>
        <Button variant="ghost" size="sm" className="w-full mt-3">
          View Full Path
        </Button>
      </CardContent>
    </Card>
  );
}
