'use client'

import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { CheckIcon, SparklesIcon } from '@heroicons/react/24/outline'
import { formatPrice } from '@/lib/utils'

interface PricingTier {
  id: string
  name: string
  description: string
  price: number
  duration_hours: number
  features: string[]
  highlighted?: boolean
  buttonText?: string
}

const pricingTiers: PricingTier[] = [
  {
    id: 'foundation',
    name: 'Foundation',
    description: 'Perfect for beginners starting their AI journey',
    price: 2500,
    duration_hours: 40,
    features: [
      '40 hours of comprehensive content',
      'Memory Architecture Basics',
      'Learning Engine Fundamentals',
      'Interactive coding labs',
      'Course completion certificate',
      'Community forum access',
      'Email support'
    ]
  },
  {
    id: 'implementation',
    name: 'Implementation',
    description: 'For developers ready to build real AI applications',
    price: 3500,
    duration_hours: 60,
    highlighted: true,
    features: [
      '60 hours of advanced content',
      'Everything in Foundation',
      'Advanced Memory Systems',
      'Industry-specific applications',
      'Production deployment training',
      'Performance optimization',
      'Priority support',
      '1-on-1 mentorship session'
    ],
    buttonText: 'Get Started'
  },
  {
    id: 'mastery',
    name: 'Mastery',
    description: 'Expert-level training for AI professionals',
    price: 5000,
    duration_hours: 40,
    features: [
      '40 hours of expert-level content',
      'Everything in Implementation',
      'Custom model development',
      'Research-level implementation',
      'Capstone project with review',
      'Lifetime access to updates',
      'Exclusive alumni network',
      'Career coaching session',
      'Industry partnerships'
    ],
    buttonText: 'Apply Now'
  }
]

const corporateTier = {
  name: 'Enterprise',
  description: 'Custom training solutions for organizations',
  price: 15000,
  min_price: 15000,
  max_price: 100000,
  features: [
    'Custom curriculum design',
    'Team progress tracking',
    'Dedicated account manager',
    'On-premise deployment option',
    'API access',
    'White-label options',
    'SLA guarantees',
    'Bulk licensing discounts'
  ]
}

export function PricingSection() {
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
            Investment in Your Future
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Choose the learning path that fits your goals. All plans include
            access to our supportive community.
          </p>
        </motion.div>

        {/* Individual Plans */}
        <div className="grid lg:grid-cols-3 gap-8 mb-16 max-w-6xl mx-auto">
          {pricingTiers.map((tier, index) => (
            <motion.div
              key={tier.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="relative"
            >
              {tier.highlighted && (
                <div className="absolute -top-4 left-0 right-0 flex justify-center">
                  <Badge variant="warning" className="shadow-lg">
                    <SparklesIcon className="w-3 h-3 mr-1" />
                    Most Popular
                  </Badge>
                </div>
              )}
              
              <Card className={`h-full ${tier.highlighted ? 'border-indigo-500 border-2 shadow-xl' : ''}`}>
                <CardHeader className="text-center pb-2">
                  <h3 className="text-xl font-bold text-slate-900 mb-2">{tier.name}</h3>
                  <p className="text-sm text-slate-500">{tier.description}</p>
                </CardHeader>
                
                <CardContent className="text-center pb-2">
                  <div className="mb-6">
                    <span className="text-4xl font-bold text-slate-900">
                      {formatPrice(tier.price)}
                    </span>
                    <span className="text-slate-500 ml-2">/ course</span>
                  </div>
                  
                  <div className="text-sm text-slate-600 mb-6">
                    {tier.duration_hours} hours of content
                  </div>

                  <ul className="space-y-3 text-left">
                    {tier.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <CheckIcon className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
                        <span className="text-slate-600">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
                
                <CardFooter className="pt-4">
                  <Button 
                    className="w-full" 
                    variant={tier.highlighted ? 'default' : 'outline'}
                    size="lg"
                  >
                    {tier.buttonText || 'Enroll Now'}
                  </Button>
                </CardFooter>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Corporate Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
        >
          <Card className="bg-slate-900 border-slate-800 max-w-4xl mx-auto">
            <CardContent className="p-8">
              <div className="grid lg:grid-cols-2 gap-8 items-center">
                <div>
                  <Badge variant="secondary" className="mb-4">Enterprise</Badge>
                  <h3 className="text-2xl font-bold text-white mb-2">
                    {corporateTier.name}
                  </h3>
                  <p className="text-slate-400 mb-4">
                    {corporateTier.description}
                  </p>
                  <div className="text-3xl font-bold text-white mb-2">
                    {formatPrice(corporateTier.min_price)} - {formatPrice(corporateTier.max_price)}
                  </div>
                  <p className="text-sm text-slate-500">
                    Custom pricing based on your organization's needs
                  </p>
                </div>
                
                <div>
                  <ul className="space-y-3 mb-6">
                    {corporateTier.features.map((feature, i) => (
                      <li key={i} className="flex items-center gap-2 text-sm text-slate-300">
                        <CheckIcon className="w-5 h-5 text-indigo-400" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                  <Button variant="secondary" className="w-full" size="lg">
                    Contact Sales
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </section>
  )
}
