import './globals.css'
import { Inter, Poppins } from 'next/font/google'
import { Providers } from '@/components/providers'
import { Toaster } from '@/components/ui/toaster'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const poppins = Poppins({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800', '900'],
  variable: '--font-poppins',
  display: 'swap',
})

export const metadata = {
  title: {
    default: 'Brain AI LMS - Learn Brain-Inspired AI',
    template: '%s | Brain AI LMS',
  },
  description: 'Master brain-inspired AI with our comprehensive learning platform. Interactive courses, hands-on labs, and real-world examples.',
  keywords: [
    'brain AI',
    'artificial intelligence',
    'machine learning',
    'neural networks',
    'memory systems',
    'learning algorithms',
    'AI education',
    'online courses',
    'interactive learning',
    'coding labs'
  ],
  authors: [{ name: 'Brain AI Team' }],
  creator: 'Brain AI Team',
  publisher: 'Brain AI Framework',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://lms.brainaiframework.com'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://lms.brainaiframework.com',
    title: 'Brain AI LMS - Learn Brain-Inspired AI',
    description: 'Master brain-inspired AI with our comprehensive learning platform. Interactive courses, hands-on labs, and real-world examples.',
    siteName: 'Brain AI LMS',
    images: [
      {
        url: '/images/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Brain AI LMS - Learn Brain-Inspired AI',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Brain AI LMS - Learn Brain-Inspired AI',
    description: 'Master brain-inspired AI with our comprehensive learning platform. Interactive courses, hands-on labs, and real-world examples.',
    images: ['/images/og-image.jpg'],
    creator: '@brainai',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
    yandex: 'your-yandex-verification-code',
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${poppins.variable}`} suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
        <meta name="theme-color" content="#3b82f6" />
        <meta name="msapplication-TileColor" content="#3b82f6" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        
        {/* Favicons and Icons */}
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        
        {/* Preload Critical Resources */}
        <link rel="preload" href="/fonts/inter-var.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
        
        {/* DNS Prefetch for External Resources */}
        <link rel="dns-prefetch" href="//api.stripe.com" />
        <link rel="dns-prefetch" href="//js.stripe.com" />
        <link rel="dns-prefetch" href="//www.google-analytics.com" />
        
        {/* Security Headers */}
        <meta httpEquiv="X-Content-Type-Options" content="nosniff" />
        <meta httpEquiv="X-Frame-Options" content="DENY" />
        <meta httpEquiv="X-XSS-Protection" content="1; mode=block" />
        <meta httpEquiv="Referrer-Policy" content="strict-origin-when-cross-origin" />
        
        {/* Performance */}
        <link rel="preconnect" href="https://res.cloudinary.com" />
        
        {/* PWA Support */}
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="Brain AI LMS" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="application-name" content="Brain AI LMS" />
        
        {/* Open Graph Image */}
        <meta property="og:image:width" content="1200" />
        <meta property="og:image:height" content="630" />
        <meta property="og:image:type" content="image/jpeg" />
        <meta property="og:site_name" content="Brain AI LMS" />
        
        {/* Twitter Card */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:image:alt" content="Brain AI LMS - Learn Brain-Inspired AI" />
        
        {/* Structured Data */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'EducationalOrganization',
              name: 'Brain AI LMS',
              description: 'Learn brain-inspired AI with comprehensive courses and interactive labs',
              url: 'https://lms.brainaiframework.com',
              logo: 'https://lms.brainaiframework.com/logo.png',
              sameAs: [
                'https://twitter.com/brainai',
                'https://github.com/brain-ai',
                'https://linkedin.com/company/brain-ai',
              ],
              offers: {
                '@type': 'Course',
                name: 'Brain AI Fundamentals',
                description: 'Introduction to brain-inspired AI and memory systems',
                provider: {
                  '@type': 'Organization',
                  name: 'Brain AI LMS',
                },
              },
            }),
          }}
        />
      </head>
      <body className={`min-h-screen bg-background font-sans antialiased ${inter.className}`}>
        <Providers>
          <div className="relative flex min-h-screen flex-col">
            <main className="flex-1">
              {children}
            </main>
          </div>
          <Toaster />
        </Providers>
        
        {/* Analytics */}
        {process.env.NODE_ENV === 'production' && (
          <>
            <script
              async
              src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`}
            />
            <script
              dangerouslySetInnerHTML={{
                __html: `
                  window.dataLayer = window.dataLayer || [];
                  function gtag(){dataLayer.push(arguments);}
                  gtag('js', new Date());
                  gtag('config', '${process.env.NEXT_PUBLIC_GA_ID}', {
                    page_title: document.title,
                    page_location: window.location.href,
                  });
                `,
              }}
            />
          </>
        )}
      </body>
    </html>
  )
}