'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { AcademicCapIcon, CheckIcon, ArrowLeftIcon } from '@heroicons/react/24/outline'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'

const forgotPasswordSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
})

type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>

export default function ForgotPasswordPage() {
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema)
  })

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setIsLoading(true)
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // In production, this would call the API
      // const response = await fetch('/api/auth/forgot-password', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(data)
      // })
      
      setIsSubmitted(true)
      toast.success('Password reset link sent to your email!')
    } catch (error) {
      toast.error('An unexpected error occurred. Please try again.')
      console.error('Forgot password error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50 flex items-center justify-center p-8">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md"
      >
        <Link 
          href="/auth/login" 
          className="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-8"
        >
          <ArrowLeftIcon className="w-5 h-5" />
          Back to login
        </Link>

        <Card className="border-0 shadow-xl">
          <CardHeader className="space-y-1 pb-6">
            <div className="flex justify-center mb-4">
              <Link href="/" className="flex items-center gap-2">
                <AcademicCapIcon className="w-10 h-10 text-indigo-600" />
              </Link>
            </div>
            
            {!isSubmitted ? (
              <>
                <CardTitle className="text-2xl font-bold text-center">Forgot Password?</CardTitle>
                <CardDescription className="text-center">
                  No worries, we&apos;ll send you a reset link
                </CardDescription>
              </>
            ) : (
              <>
                <CardTitle className="text-2xl font-bold text-center text-emerald-600">
                  Check Your Email
                </CardTitle>
                <CardDescription className="text-center">
                  We&apos;ve sent a password reset link
                </CardDescription>
              </>
            )}
          </CardHeader>
          
          <CardContent>
            {!isSubmitted ? (
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div className="space-y-2">
                  <label htmlFor="email" className="text-sm font-medium text-slate-700">
                    Email Address
                  </label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    {...register('email')}
                    error={errors.email?.message}
                  />
                  <p className="text-xs text-slate-500">
                    Enter the email address associated with your account
                  </p>
                </div>

                <Button
                  type="submit"
                  className="w-full"
                  size="lg"
                  isLoading={isLoading}
                >
                  Send Reset Link
                </Button>
              </form>
            ) : (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center space-y-6"
              >
                <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto">
                  <CheckIcon className="w-8 h-8 text-emerald-600" />
                </div>
                
                <div className="space-y-2">
                  <p className="text-slate-600">
                    We&apos;ve sent a password reset link to:
                  </p>
                  <p className="font-medium text-slate-900">
                    your.email@example.com
                  </p>
                </div>

                <div className="bg-slate-50 rounded-lg p-4 text-sm text-slate-600">
                  <p>Didn&apos;t receive the email? Check your spam filter or try another email address.</p>
                </div>

                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => setIsSubmitted(false)}
                >
                  Try another email
                </Button>
              </motion.div>
            )}

            <div className="mt-6 text-center text-sm text-slate-600">
              Remember your password?{' '}
              <Link href="/auth/login" className="text-indigo-600 hover:text-indigo-500 font-medium">
                Sign in
              </Link>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
