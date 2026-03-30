import type { Metadata } from 'next'
import './globals.css'
import { ThemeProvider } from './ThemeContext'

export const metadata: Metadata = {
  title: 'AI Banking Assistant - UAE Bank',
  description: 'Modern AI-powered banking customer support chatbot with bilingual Arabic/English support',
  icons: {
    icon: [
      {
        url: '/favicon.svg',
        type: 'image/svg+xml',
      },
    ],
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning className="transition-colors duration-300 min-h-screen w-full">
      <head>
        <script src="/theme-init.js" />
      </head>
      <body suppressHydrationWarning className="antialiased transition-colors duration-300 min-h-screen w-full overflow-x-hidden">
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
