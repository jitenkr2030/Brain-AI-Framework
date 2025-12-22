'use client';

import { useState, useRef, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { useSmartSearch } from '@/hooks/use-brain-ai';
import type { SearchResult } from '@/types/brain-ai';

interface SmartSearchBarProps {
  userContext?: {
    userId: string;
    currentCourse?: string;
    currentModule?: string;
  };
  scope?: 'all' | 'courses' | 'content' | 'discussions';
  placeholder?: string;
  onSearch?: (query: string, results: SearchResult[]) => void;
  onResultClick?: (result: SearchResult) => void;
  isModal?: boolean;
}

export function SmartSearchBar({
  userContext,
  scope = 'all',
  placeholder = 'Ask a question or search for courses...',
  onSearch,
  onResultClick,
  isModal = false,
}: SmartSearchBarProps) {
  const {
    query,
    results,
    isSearching,
    searchTime,
    setQuery,
    search,
    clearResults,
  } = useSmartSearch({ userContext });

  const [isFocused, setIsFocused] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsFocused(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      await search(query);
      onSearch?.(query, results);
    }
  };

  const handleResultClick = (result: SearchResult) => {
    onResultClick?.(result);
    setIsFocused(false);
    setQuery('');
    clearResults();
  };

  const getResultIcon = (type: string) => {
    switch (type) {
      case 'video_lecture':
        return '🎬';
      case 'text_module':
        return '📄';
      case 'course':
        return '📚';
      case 'discussion':
        return '💬';
      default:
        return '🔍';
    }
  };

  return (
    <div ref={searchRef} className="relative w-full">
      <form onSubmit={handleSubmit}>
        <div className="relative">
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
          <Input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setIsFocused(true)}
            placeholder={placeholder}
            className="pl-10 pr-20 py-3 text-lg border-2 focus:border-indigo-500"
          />
          <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
            <Button
              type="submit"
              size="sm"
              disabled={!query.trim() || isSearching}
              className="bg-indigo-600 hover:bg-indigo-700"
            >
              {isSearching ? (
                <svg
                  className="animate-spin h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
              ) : (
                'Search'
              )}
            </Button>
          </div>
        </div>
      </form>

      {/* Search Results Dropdown */}
      {isFocused && (query || results.length > 0) && (
        <Card className="absolute z-50 w-full mt-2 max-h-96 overflow-y-auto">
          <CardContent className="p-0">
            {isSearching ? (
              <div className="p-4 space-y-3">
                <div className="flex items-center justify-center">
                  <svg
                    className="animate-spin h-6 w-6 text-indigo-600"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                </div>
                <p className="text-center text-sm text-gray-500">
                  AI is analyzing your search...
                </p>
                {[1, 2, 3].map((i) => (
                  <div key={i} className="space-y-2">
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-3 w-full" />
                  </div>
                ))}
              </div>
            ) : results.length > 0 ? (
              <div className="divide-y">
                <div className="px-4 py-2 bg-gray-50 flex items-center justify-between">
                  <span className="text-xs text-gray-500">
                    {results.length} results found in {searchTime}ms
                  </span>
                  <Badge variant="secondary">AI Powered</Badge>
                </div>
                {results.map((result) => (
                  <button
                    key={result.result_id}
                    onClick={() => handleResultClick(result)}
                    className="w-full p-4 text-left hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start space-x-3">
                      <span className="text-xl">{getResultIcon(result.type)}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <h4 className="font-medium text-gray-900 truncate">
                            {result.title}
                          </h4>
                          <Badge variant="outline" className="text-xs">
                            {result.type.replace('_', ' ')}
                          </Badge>
                        </div>
                        {result.course && (
                          <p className="text-sm text-gray-500 mt-0.5">
                            From: {result.course}
                          </p>
                        )}
                        <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                          {result.snippet}
                        </p>
                        <div className="flex items-center space-x-2 mt-1">
                          <span
                            className={`text-xs px-2 py-0.5 rounded ${
                              result.relevance_score >= 0.9
                                ? 'bg-green-100 text-green-700'
                                : result.relevance_score >= 0.7
                                ? 'bg-blue-100 text-blue-700'
                                : 'bg-yellow-100 text-yellow-700'
                            }`}
                          >
                            {Math.round(result.relevance_score * 100)}% match
                          </span>
                          {result.timestamp && (
                            <span className="text-xs text-gray-400">
                              @ {result.timestamp}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            ) : query ? (
              <div className="p-8 text-center">
                <span className="text-4xl mb-2 block">🔍</span>
                <p className="text-gray-600">No results found for "{query}"</p>
                <p className="text-sm text-gray-500 mt-1">
                  Try rephrasing your question or using different keywords
                </p>
              </div>
            ) : null}
          </CardContent>
        </Card>
      )}

      {/* AI Search Tips */}
      {isFocused && !query && (
        <Card className="absolute z-50 w-full mt-2">
          <CardContent className="p-4">
            <p className="text-xs font-medium text-gray-500 mb-2">
              💡 Try asking:
            </p>
            <div className="space-y-1">
              {[
                'How do I fix a React useEffect dependency warning?',
                'Best resources for learning machine learning',
                'Explain neural networks in simple terms',
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => {
                    setQuery(suggestion);
                    search(suggestion);
                  }}
                  className="block w-full text-left text-sm text-gray-600 hover:text-indigo-600 hover:bg-gray-50 px-2 py-1 rounded"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// Compact version for header use
export function CompactSmartSearch({
  onSearchClick,
}: {
  onSearchClick?: () => void;
}) {
  return (
    <button
      onClick={onSearchClick}
      className="flex items-center space-x-2 px-4 py-2 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors"
    >
      <svg
        className="w-4 h-4 text-gray-500"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
      <span className="text-sm text-gray-500">Search courses...</span>
      <span className="text-xs text-gray-400 border border-gray-300 rounded px-1.5 py-0.5">
        ⌘K
      </span>
    </button>
  );
}
