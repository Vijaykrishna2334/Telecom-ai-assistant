import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-primary-600 text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="text-2xl font-bold">📞</div>
            <div>
              <h1 className="text-2xl font-bold">Telecom AI Assistant</h1>
              <p className="text-sm text-primary-100">Your intelligent support companion</p>
            </div>
          </div>
          <nav className="hidden md:flex space-x-6">
            <a href="#" className="hover:text-primary-200 transition">Chat</a>
            <a href="#" className="hover:text-primary-200 transition">Plans</a>
            <a href="#" className="hover:text-primary-200 transition">Help</a>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
