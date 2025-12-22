'use client'

import { motion } from 'framer-motion'
import { Card, CardContent } from '@/components/ui/card'
import { Avatar } from '@/components/ui/avatar'
import { StarIcon } from '@heroicons/react/24/solid'

interface Testimonial {
  id: string
  name: string
  role: string
  company: string
  avatar_url?: string
  content: string
  rating: number
  course_title?: string
}

const testimonials: Testimonial[] = [
  {
    id: '1',
    name: 'Sarah Chen',
    role: 'Senior ML Engineer',
    company: 'Tech Giants Inc.',
    content: 'The Brain AI LMS transformed my career. The hands-on labs and expert mentorship helped me transition from traditional ML to cutting-edge brain-inspired AI systems. Within 6 months, I was leading AI initiatives at my company.',
    rating: 5,
    course_title: 'Mastery Level Program'
  },
  {
    id: '2',
    name: 'Michael Rodriguez',
    role: 'AI Research Scientist',
    company: 'DeepMind',
    content: 'Finally, a course that goes beyond theory. Building actual working memory systems and learning engines gave me practical skills that directly apply to my research. The community here is incredibly supportive.',
    rating: 5,
    course_title: 'Implementation Level Program'
  },
  {
    id: '3',
    name: 'Emily Watson',
    role: 'Data Science Lead',
    company: 'Fortune 500 Company',
    content: 'As someone who has tried many online courses, Brain AI LMS stands out. The interactive code execution environment and real-time feedback accelerated my learning curve dramatically. Highly recommended!',
    rating: 5,
    course_title: 'Foundation Level Program'
  }
]

export function Testimonials() {
  return (
    <section className="section bg-slate-50">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            What Our Students Say
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Join thousands of successful professionals who have transformed their careers
            with Brain AI education.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={testimonial.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="h-full">
                <CardContent className="p-6">
                  {/* Rating */}
                  <div className="flex gap-1 mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <StarIcon key={i} className="w-5 h-5 text-amber-400 fill-amber-400" />
                    ))}
                  </div>

                  {/* Content */}
                  <p className="text-slate-600 mb-6 leading-relaxed">
                    "{testimonial.content}"
                  </p>

                  {/* Course Badge */}
                  {testimonial.course_title && (
                    <div className="mb-4">
                      <span className="text-xs font-medium text-indigo-600 bg-indigo-50 px-2 py-1 rounded">
                        {testimonial.course_title}
                      </span>
                    </div>
                  )}

                  {/* Author */}
                  <div className="flex items-center gap-3 pt-4 border-t border-slate-100">
                    <Avatar
                      src={testimonial.avatar_url}
                      name={testimonial.name}
                      size="sm"
                    />
                    <div>
                      <div className="font-medium text-slate-900">
                        {testimonial.name}
                      </div>
                      <div className="text-sm text-slate-500">
                        {testimonial.role} at {testimonial.company}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
