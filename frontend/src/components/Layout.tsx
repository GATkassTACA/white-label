import React from 'react'
import { BrandingConfig } from '@/types'

interface LayoutProps {
  children: React.ReactNode
  branding: BrandingConfig
}

export default function Layout({ children, branding }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Dynamic CSS variables for theming */}
      <style>
        {`
          :root {
            --color-primary-500: ${branding.primary_color};
            --color-primary-600: ${branding.primary_color}dd;
            --color-primary-700: ${branding.primary_color}bb;
          }
        `}
      </style>
      
      {/* Header */}
      <header className="bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            {/* Logo and Title */}
            <div className="flex items-center space-x-4">
              {branding.logo_url ? (
                <img 
                  src={branding.logo_url} 
                  alt={branding.company_name}
                  className="h-10 w-10 rounded-full object-cover"
                />
              ) : (
                <div className="h-10 w-10 rounded-full bg-white/20 flex items-center justify-center">
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
                  </svg>
                </div>
              )}
              <div>
                <h1 className="text-xl font-semibold">{branding.company_name}</h1>
                <p className="text-sm opacity-90">Modern Chat Platform</p>
              </div>
            </div>
            
            {/* Navigation */}
            <nav className="hidden md:flex space-x-4">
              <a 
                href="/chat" 
                className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
              >
                Chat
              </a>
              <a 
                href="/documents" 
                className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
              >
                Documents
              </a>
              <a 
                href="/wizard" 
                className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
              >
                Branding
              </a>
            </nav>
            
            {/* Mobile menu button */}
            <button className="md:hidden p-2 rounded-lg bg-white/10 hover:bg-white/20">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>
      
      {/* Footer */}
      <footer className="bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500">
            {branding.footer_text}
          </div>
        </div>
      </footer>
    </div>
  )
}
