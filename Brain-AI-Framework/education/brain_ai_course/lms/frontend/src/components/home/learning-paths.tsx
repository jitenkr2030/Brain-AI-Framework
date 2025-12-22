'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Card, CardContent } from '@/components/ui/card'
import { ArrowRightIcon, CheckIcon } from '@heroicons/react/24/outline'

interface LearningPath {
  id: string
  title: string
  description: string
  courses_count: number
  duration_hours: number
  level: string
  color: string
  features: string[]
}

const learningPaths: LearningPath[] = [
  {
    id: 'foundation',
    title: 'Foundation',
    description: 'Start your journey with Brain AI fundamentals. Perfect for beginners with basic programming knowledge.',
    courses_count: 3,
    duration_hours: 40,
    level: 'Beginner',
    color: 'from-emerald-500 to-teal-600',
    features: [
      'Memory Architecture Basics',
      'Neural Network Fundamentals',
      'Python Programming',
      'Learning Engine Introduction'
    ]
  },
  {
    id: 'implementation',
    title: 'Implementation',
    description: 'Build on your foundation with advanced memory systems and real-world application development.',
    courses_count: 4,
    duration_hours: 60,
    level: 'Intermediate',
    color: 'from-blue-500 to-indigo-600',
    features: [
      'Advanced Memory Systems',
      'Industry Applications',
      'Production Deployment',
      'Performance Optimization'
    ]
  },
  {
    id: 'mastery',
    title: 'Mastery',
    description: 'Master cutting-edge AI techniques, custom model development, and research-level implementation.',
    courses_count: 3,
    duration_hours: 40,
    level: 'Advanced',
    color: 'from-purple-500 to-violet-600',
    features: [
      'Advanced AI Techniques',
      'Custom Model Development',
      'Research-Level Implementation',
      'Capstone Project'
    ]
  }
]

export function LearningPaths() {
  return (
    <section className="section bg-white">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            Structured Learning Paths
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Follow our carefully designed paths from foundation to mastery, with
            hands-on projects and expert guidance at every step.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {learningPaths.map((path, index) => (
            <motion.div
              key={path.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="h-full overflow-hidden" hoverable>
                {/* Header */}
                <div className={`bg-gradient-to-br ${path.color} p-6 text-white`}>
                  <div className="text-sm font-medium opacity-80 mb-2">
                    {path.courses_count} Courses • {path.duration_hours} Hours
                  </div>
                  <h3 className="text-2xl font-bold mb-2">{path.title}</h3>
                  <p className="text-white/80 text-sm">{path.description}</p>
                </div>

                <CardContent className="p-6">
                  {/* Features List */}
                  <ul className="space-y-3 mb-6">
                    {path.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <CheckIcon className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
                        <span className="text-slate-600">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {/* CTA */}
                  <Link
                    href={`/learning-paths/${path.id}`}
                    className="inline-flex items-center justify-center w-full gap-2 px-4 py-2 rounded-lg bg-slate-100 text-slate-700 font-medium hover:bg-slate-200 transition-colors"
                  >
                    Explore {path.title}
                    <ArrowRightIcon className="w-4 h-4" />
                  </Link>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
