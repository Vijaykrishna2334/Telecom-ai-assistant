import { useState, useEffect } from 'react';
import './styles/globals.css';
import LandingPage from './components/Landing/LandingPage';
import ChatPage from './components/Chat/ChatPage';

function App() {
  const [currentPage, setCurrentPage] = useState<'landing' | 'chat'>('landing');

  useEffect(() => {
    // Simple routing based on pathname
    const path = window.location.pathname;
    if (path === '/chat') {
      setCurrentPage('chat');
    } else {
      setCurrentPage('landing');
    }

    // Handle navigation events
    const handlePopState = () => {
      const path = window.location.pathname;
      if (path === '/chat') {
        setCurrentPage('chat');
      } else {
        setCurrentPage('landing');
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Override window.location.href to handle client-side navigation
  useEffect(() => {
    const originalPushState = window.history.pushState;
    const originalReplaceState = window.history.replaceState;

    window.history.pushState = function (...args) {
      originalPushState.apply(window.history, args);
      window.dispatchEvent(new Event('popstate'));
    };

    window.history.replaceState = function (...args) {
      originalReplaceState.apply(window.history, args);
      window.dispatchEvent(new Event('popstate'));
    };

    // Intercept link clicks
    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === 'A' || target.closest('a')) {
        const link = (target.tagName === 'A' ? target : target.closest('a')) as HTMLAnchorElement;
        const href = link.getAttribute('href');

        if (href && (href === '/chat' || href === '/')) {
          e.preventDefault();
          window.history.pushState({}, '', href);
          setCurrentPage(href === '/chat' ? 'chat' : 'landing');
        }
      }

      if (target.tagName === 'BUTTON' && target.getAttribute('onclick')?.includes('window.location.href')) {
        e.preventDefault();
        const match = target.getAttribute('onclick')?.match(/['"]([^'"]+)['"]/);
        if (match) {
          const href = match[1];
          if (href === '/chat' || href === '/') {
            window.history.pushState({}, '', href);
            setCurrentPage(href === '/chat' ? 'chat' : 'landing');
          }
        }
      }
    };

    document.addEventListener('click', handleClick);

    return () => {
      document.removeEventListener('click', handleClick);
      window.history.pushState = originalPushState;
      window.history.replaceState = originalReplaceState;
    };
  }, []);

  return currentPage === 'landing' ? <LandingPage /> : <ChatPage />;
}

export default App;

