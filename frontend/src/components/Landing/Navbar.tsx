import { useState } from 'react';

const Navbar = () => {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const scrollToSection = (sectionId: string) => {
        const element = document.getElementById(sectionId);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
            setMobileMenuOpen(false);
        }
    };

    return (
        <nav className="fixed w-full top-0 z-50 bg-black/80 backdrop-blur-md border-b border-white/10">
            <div className="container mx-auto px-4">
                <div className="flex items-center justify-between h-20">
                    {/* Logo */}
                    <div className="flex items-center space-x-3 cursor-pointer" onClick={() => window.location.href = '/'}>
                        <div className="w-10 h-10 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-lg flex items-center justify-center text-2xl">
                            📞
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-white">Telecom AI</h1>
                            <p className="text-xs text-gray-400">Smart Assistant</p>
                        </div>
                    </div>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center space-x-8">
                        <button
                            onClick={() => scrollToSection('features')}
                            className="text-gray-300 hover:text-white cursor-pointer transition-colors"
                        >
                            Features
                        </button>
                        <button
                            onClick={() => scrollToSection('capabilities')}
                            className="text-gray-300 hover:text-white cursor-pointer transition-colors"
                        >
                            Capabilities
                        </button>
                        <button
                            onClick={() => scrollToSection('about')}
                            className="text-gray-300 hover:text-white cursor-pointer transition-colors"
                        >
                            About
                        </button>
                        <button
                            onClick={() => window.location.href = '/chat'}
                            className="px-6 py-2.5 bg-white text-black font-semibold rounded-full hover:bg-gray-200 transition-all flex items-center space-x-2"
                        >
                            <span>START FOR FREE</span>
                            <span>→</span>
                        </button>
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        className="md:hidden text-white p-2"
                    >
                        <svg
                            className="w-6 h-6"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            {mobileMenuOpen ? (
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M6 18L18 6M6 6l12 12"
                                />
                            ) : (
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M4 6h16M4 12h16M4 18h16"
                                />
                            )}
                        </svg>
                    </button>
                </div>

                {/* Mobile Menu */}
                {mobileMenuOpen && (
                    <div className="md:hidden py-4 space-y-4">
                        <button
                            onClick={() => scrollToSection('features')}
                            className="block text-gray-300 hover:text-white cursor-pointer transition-colors w-full text-left"
                        >
                            Features
                        </button>
                        <button
                            onClick={() => scrollToSection('capabilities')}
                            className="block text-gray-300 hover:text-white cursor-pointer transition-colors w-full text-left"
                        >
                            Capabilities
                        </button>
                        <button
                            onClick={() => scrollToSection('about')}
                            className="block text-gray-300 hover:text-white cursor-pointer transition-colors w-full text-left"
                        >
                            About
                        </button>
                        <button
                            onClick={() => window.location.href = '/chat'}
                            className="block px-6 py-2.5 bg-white text-black font-semibold rounded-full hover:bg-gray-200 transition-all text-center"
                        >
                            START FOR FREE →
                        </button>
                    </div>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
