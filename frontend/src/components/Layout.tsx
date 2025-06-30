import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { CompareProvider } from '../context/CompareContext'
import CompareBar from './CompareBar'
import HelpButton from './HelpButton'

interface LayoutProps {
  children: React.ReactNode
}

const navigation = [
  { name: 'Browse Strains', href: '/strains' },
  { name: 'Identify Strain', href: '/identify' },
  { name: 'Help', href: '/help' },
  { name: 'About', href: '/about' },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  
  // Hide help button on help-related pages
  const hideHelpButton = ['/help', '/faq'].includes(location.pathname)

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="bg-white border-b border-border sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center group">
              <div className="h-8 w-8 bg-primary rounded-lg flex items-center justify-center transition-transform duration-300 group-hover:scale-110">
                <span className="text-primary-foreground font-bold text-sm">🧬</span>
              </div>
              <div className="ml-3">
                <h1 className="text-lg font-bold text-foreground">LysoData-Miner</h1>
                <p className="text-xs text-muted-foreground">Lysobacter Strain Database</p>
              </div>
            </Link>

            {/* Navigation */}
            <nav className="flex space-x-2">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`inline-flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                      isActive
                        ? 'bg-primary/10 text-primary font-semibold'
                        : 'text-muted-foreground hover:text-primary hover:bg-primary/10'
                    }`}
                  >
                    {item.name}
                  </Link>
                )
              })}
            </nav>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <CompareProvider>
          {children}
          <CompareBar />
          {!hideHelpButton && <HelpButton />}
        </CompareProvider>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-muted-foreground text-sm">
            <p>&copy; 2024 LysoData-Miner. Scientific database for Lysobacter strain identification.</p>
          </div>
        </div>
      </footer>
    </div>
  )
} 