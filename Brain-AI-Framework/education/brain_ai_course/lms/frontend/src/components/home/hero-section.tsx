'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { ArrowRightIcon, PlayCircleIcon, CodeBracketIcon, AcademicCapIcon } from '@heroicons/react/24/outline'

interface HeroSectionProps {
  user?: { name: string } | null
}

export function HeroSection({ user }: HeroSectionProps) {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }} />
      </div>

      <div className="container relative mx-auto px-4 py-20 lg:py-32">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm mb-6">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
              </span>
              <span className="text-sm font-medium">Next Cohort Starting Soon</span>
            </div>

            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight mb-6">
              Master{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">
                Brain-Inspired AI
              </span>
              {' '}Development
            </h1>

            <p className="text-lg md:text-xl text-slate-300 mb-8 max-w-xl">
              Learn to build intelligent systems inspired by how the human brain works.
              Comprehensive courses from foundation to mastery level with hands-on labs
              and expert mentorship.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 mb-12">
              <Button size="lg" asChild>
                <Link href="/courses">
                  Explore Courses
                  <ArrowRightIcon className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="border-white/30 text-white hover:bg-white/10 hover:text-white">
                <PlayCircleIcon className="mr-2 h-5 w-5" />
                Watch Demo
              </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-6 pt-8 border-t border-white/10">
              <div>
                <div className="text-2xl font-bold">10K+</div>
                <div className="text-sm text-slate-400">Active Learners</div>
              </div>
              <div>
                <div className="text-2xl font-bold">25+</div>
                <div className="text-sm text-slate-400">Courses</div>
              </div>
              <div>
                <div className="text-2xl font-bold">5K+</div>
                <div className="text-sm text-slate-400">Certificates</div>
              </div>
            </div>
          </motion.div>

          {/* Right Content - Visual Element */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="relative"
          >
            <div className="relative z-10 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-6 shadow-2xl">
              {/* Code Preview */}
              <div className="flex items-center gap-2 mb-4">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                </div>
                <span className="text-sm text-slate-400">brain_ai_example.py</span>
              </div>
              
              <pre className="text-sm text-slate-300 overflow-x-auto">
                <code>{`from brain_ai import Memory, LearningEngine

# Initialize brain-inspired memory
memory = Memory(
    memory_type="episodic",
    capacity=10000
)

# Create learning engine
engine = LearningEngine(
    memory=memory,
    learning_rate=0.001
)

# Train on new data
engine.learn(dataset, epochs=100)

# Get intelligent predictions
predictions = engine.predict(input_data)`}</code>
              </pre>

              {/* Floating badges */}
              <div className="absolute -top-4 -right-4 bg-emerald-500 text-white px-4 py-2 rounded-full text-sm font-medium shadow-lg">
                <CodeBracketIcon className="inline h-4 w-4 mr-1" />
                Interactive Labs
              </div>
              <div className="absolute -bottom-4 -left-4 bg-indigo-500 text-white px-4 py-2 rounded-full text-sm font-medium shadow-lg">
                <AcademicCapIcon className="inline h-4 w-4 mr-1" />
                Expert Certified
              </div>
            </div>

            {/* Decorative blobs */}
            <div className="absolute -top-20 -right-20 w-64 h-64 bg-indigo-500/30 rounded-full blur-3xl" />
            <div className="absolute -bottom-20 -left-20 w-64 h-64 bg-cyan-500/30 rounded-full blur-3xl" />
          </motion.div>
        </div>
      </div>

      {/* Bottom gradient */}
      <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-white to-transparent" />
    </section>
  )
}
