'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { MagnifyingGlassIcon, FunnelIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/select'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { CourseCard } from '@/components/home/course-card'
import { useCourses } from '@/hooks/use-courses'

const levels = [
  { value: '', label: 'All Levels' },
  { value: 'foundation', label: 'Foundation' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' },
  { value: 'expert', label: 'Expert' },
]

const categories = [
  { value: '', label: 'All Categories' },
  { value: 'brain_ai_fundamentals', label: 'Brain AI Fundamentals' },
  { value: 'memory_systems', label: 'Memory Systems' },
  { value: 'learning_engines', label: 'Learning Engines' },
  { value: 'industry_applications', label: 'Industry Applications' },
  { value: 'enterprise_deployment', label: 'Enterprise Deployment' },
]

const sortOptions = [
  { value: 'popular', label: 'Most Popular' },
  { value: 'newest', label: 'Newest' },
  { value: 'price_low', label: 'Price: Low to High' },
  { value: 'price_high', label: 'Price: High to Low' },
  { value: 'rating', label: 'Highest Rated' },
]

export default function CourseCatalogPage() {
  const { courses, isLoading, total, searchCourses } = useCourses()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedLevel, setSelectedLevel] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [sortBy, setSortBy] = useState('popular')
  const [showFilters, setShowFilters] = useState(false)
  const [isFiltersApplied, setIsFiltersApplied] = useState(false)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    searchCourses({
      search: searchQuery,
      level: selectedLevel || undefined,
      category: selectedCategory || undefined
    })
    setIsFiltersApplied(true)
  }

  const clearFilters = () => {
    setSearchQuery('')
    setSelectedLevel('')
    setSelectedCategory('')
    setIsFiltersApplied(false)
    searchCourses({})
  }

  const activeFiltersCount = [
    selectedLevel,
    selectedCategory,
    searchQuery
  ].filter(Boolean).length

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Course Catalog</h1>
              <p className="text-slate-600 mt-1">
                {total} courses available to help you master brain-inspired AI
              </p>
            </div>
            <Link href="/" className="text-indigo-600 hover:text-indigo-700 font-medium">
              ← Back to Home
            </Link>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Search and Filters Bar */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 mb-8">
          <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
            {/* Search Input */}
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Search courses..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>

            {/* Desktop Filters */}
            <div className="hidden md:flex gap-4">
              <select
                value={selectedLevel}
                onChange={(e) => setSelectedLevel(e.target.value)}
                className="px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
              >
                {levels.map((level) => (
                  <option key={level.value} value={level.value}>
                    {level.label}
                  </option>
                ))}
              </select>

              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
              >
                {categories.map((category) => (
                  <option key={category.value} value={category.value}>
                    {category.label}
                  </option>
                ))}
              </select>

              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
              >
                {sortOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>

              <Button type="submit">
                <FunnelIcon className="w-4 h-4 mr-2" />
                Apply Filters
              </Button>
            </div>

            {/* Mobile Filter Toggle */}
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
              className="md:hidden"
            >
              <FunnelIcon className="w-4 h-4 mr-2" />
              Filters {activeFiltersCount > 0 && `(${activeFiltersCount})`}
            </Button>
          </form>

          {/* Mobile Filters */}
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden mt-4 pt-4 border-t border-slate-200 space-y-4"
            >
              <select
                value={selectedLevel}
                onChange={(e) => setSelectedLevel(e.target.value)}
                className="w-full px-4 py-3 border border-slate-300 rounded-lg bg-white"
              >
                {levels.map((level) => (
                  <option key={level.value} value={level.value}>
                    {level.label}
                  </option>
                ))}
              </select>

              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-4 py-3 border border-slate-300 rounded-lg bg-white"
              >
                {categories.map((category) => (
                  <option key={category.value} value={category.value}>
                    {category.label}
                  </option>
                ))}
              </select>

              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full px-4 py-3 border border-slate-300 rounded-lg bg-white"
              >
                {sortOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>

              <div className="flex gap-4">
                <Button type="submit" className="flex-1">
                  Apply Filters
                </Button>
                {isFiltersApplied && (
                  <Button type="button" variant="outline" onClick={clearFilters}>
                    Clear All
                  </Button>
                )}
              </div>
            </motion.div>
          )}

          {/* Active Filters */}
          {isFiltersApplied && (
            <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-slate-200">
              <span className="text-sm text-slate-500 py-1">Active filters:</span>
              {searchQuery && (
                <Badge variant="secondary" className="gap-1">
                  Search: {searchQuery}
                  <button onClick={() => setSearchQuery('')}>
                    <XMarkIcon className="w-3 h-3" />
                  </button>
                </Badge>
              )}
              {selectedLevel && (
                <Badge variant="secondary" className="gap-1">
                  Level: {selectedLevel}
                  <button onClick={() => setSelectedLevel('')}>
                    <XMarkIcon className="w-3 h-3" />
                  </button>
                </Badge>
              )}
              {selectedCategory && (
                <Badge variant="secondary" className="gap-1">
                  Category: {selectedCategory}
                  <button onClick={() => setSelectedCategory('')}>
                    <XMarkIcon className="w-3 h-3" />
                  </button>
                </Badge>
              )}
              <button
                onClick={clearFilters}
                className="text-sm text-indigo-600 hover:text-indigo-700 ml-2"
              >
                Clear all
              </button>
            </div>
          )}
        </div>

        {/* Results */}
        {isLoading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="bg-slate-200 rounded-xl h-48 mb-4" />
                <div className="bg-slate-200 h-4 rounded mb-2 w-3/4" />
                <div className="bg-slate-200 h-4 rounded mb-4 w-1/2" />
                <div className="bg-slate-200 h-8 rounded w-1/3" />
              </div>
            ))}
          </div>
        ) : courses.length === 0 ? (
          <Card className="text-center py-16">
            <div className="max-w-md mx-auto">
              <MagnifyingGlassIcon className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-900 mb-2">
                No courses found
              </h3>
              <p className="text-slate-600 mb-6">
                Try adjusting your search or filters to find what you&apos;re looking for.
              </p>
              <Button variant="outline" onClick={clearFilters}>
                Clear all filters
              </Button>
            </div>
          </Card>
        ) : (
          <>
            <div className="flex items-center justify-between mb-6">
              <p className="text-slate-600">
                Showing <span className="font-medium">{courses.length}</span> of{' '}
                <span className="font-medium">{total}</span> courses
              </p>
            </div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
            >
              {courses.map((course, index) => (
                <motion.div
                  key={course.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <CourseCard course={course} />
                </motion.div>
              ))}
            </motion.div>
          </>
        )}
      </div>
    </div>
  )
}
