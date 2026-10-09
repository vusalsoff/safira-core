import { Link, useLocation } from 'react-router-dom';
import { Database, Menu, X } from 'lucide-react';
import { useState, useEffect } from 'react';
import { cn } from '../../utils/cn';
import SpiderWeb from '../ui/SpiderWeb';
import ThemeToggle from '../ui/ThemeToggle';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Architecture & Modes', path: '/modes' },
    { name: 'Live Engine', path: '/engine' },
    { name: 'About Project', path: '/about' },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-darker/70 backdrop-blur-2xl border-b border-surface-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          <Link to="/" className="flex items-center gap-3 group shrink-0">
            <div className="relative">
              <div className="absolute -inset-2 bg-primary/20 blur-lg rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <Database className="h-8 w-8 text-primary relative z-10" />
            </div>
            <span className="text-2xl font-bold tracking-widest text-white">SAFIRA</span>
          </Link>
          <div className="hidden md:flex space-x-1 flex-1 justify-center">
            {navLinks.map((link) => {
              const isActive = location.pathname === link.path;
              return (
                <Link
                  key={link.name}
                  to={link.path}
                  className={cn(
                    "relative px-4 py-2 rounded-full text-sm font-medium transition-all duration-300",
                    isActive ? "text-white bg-surface shadow-sm border border-surface-border" : "text-gray-400 hover:text-white hover:bg-surface border border-transparent"
                  )}
                >
                  {link.name}
                </Link>
              );
            })}
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <ThemeToggle />
            <div className="md:hidden">
              <button onClick={() => setIsOpen(!isOpen)} className="p-2 text-gray-400 hover:text-white transition-colors glass-panel rounded-full">
                {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Mobile Menu */}
      <div className={cn(
        "md:hidden absolute w-full bg-darker/95 backdrop-blur-3xl border-b border-surface-border transition-all duration-300 overflow-hidden",
        isOpen ? "max-h-96 border-b opacity-100" : "max-h-0 border-transparent opacity-0"
      )}>
        <div className="px-4 py-4 space-y-2">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              to={link.path}
              onClick={() => setIsOpen(false)}
              className={cn(
                "block px-4 py-3 rounded-xl text-base font-medium transition-all",
                location.pathname === link.path 
                  ? "text-white bg-primary/20 border border-primary/30" 
                  : "text-gray-400 hover:text-white hover:bg-white/5 border border-transparent"
              )}
            >
              {link.name}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
};

const Footer = () => (
  <footer className="border-t border-surface-border py-12 mt-auto relative z-10 bg-darker/50 backdrop-blur-sm">
    <div className="max-w-7xl mx-auto px-4 text-center">
      <div className="inline-flex items-center gap-2 text-primary font-semibold mb-4">
        <Database className="h-5 w-5" /> SAFIRA
      </div>
      <p className="text-sm text-gray-500 max-w-md mx-auto mb-2">
        Semantic Architecture for Information Refinement and Access
      </p>
      <p className="text-xs text-gray-600">
        &copy; 2026 | NeuroBridge.SI Hackathon, Baku, Azerbaijan
      </p>
    </div>
  </footer>
);

export default function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden">
      <SpiderWeb />
      <Navbar />
      <main className="flex-grow pt-20 relative z-10 w-full">
        {children}
      </main>
      <Footer />
    </div>
  );
}
