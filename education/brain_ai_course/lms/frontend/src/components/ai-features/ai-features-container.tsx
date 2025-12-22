'use client';

import { useAuth } from '@/hooks/use-auth';
import { SmartSearchBar, AiTutorWidget } from '@/components/ai-features';

export function AiFeaturesContainer() {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return null;
  }

  return (
    <>
      {/* Smart Search Bar - Placed prominently in the header area */}
      <div className="w-full max-w-2xl mx-auto mb-6">
        <SmartSearchBar
          userContext={
            user
              ? {
                  userId: user.id,
                }
              : undefined
          }
          scope="all"
          placeholder="Ask questions, search courses, find resources..."
        />
      </div>

      {/* AI Tutor Widget - Floating for easy access */}
      {isAuthenticated && user && (
        <AiTutorWidget
          userId={user.id}
          position="bottom-right"
          defaultOpen={false}
        />
      )}
    </>
  );
}
