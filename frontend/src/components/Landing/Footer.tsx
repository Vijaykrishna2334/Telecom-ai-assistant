const Footer = () => {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="bg-black border-t border-white/10 py-16">
            <div className="container">
                <div className="grid md:grid-cols-4 gap-12 mb-12">
                    {/* Brand */}
                    <div className="col-span-1">
                        <div className="flex items-center space-x-3 mb-6">
                            <div className="w-10 h-10 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-lg flex items-center justify-center text-2xl">
                                📞
                            </div>
                            <div>
                                <h3 className="text-lg font-bold text-white">Telecom AI</h3>
                                <p className="text-xs text-gray-400">Smart Assistant</p>
                            </div>
                        </div>
                        <p className="text-gray-400 text-sm font-light leading-relaxed">
                            AI-powered voice and chat assistant for modern telecom businesses.
                        </p>
                    </div>

                    {/* Solutions */}
                    <div>
                        <h4 className="text-white font-semibold mb-6 text-sm uppercase tracking-wider">Solutions</h4>
                        <ul className="space-y-3">
                            <li>
                                <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors font-light">
                                    Customer Support
                                </a>
                            </li>
                            <li>
                                <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors font-light">
                                    Plan Management
                                </a>
                            </li>
                            <li>
                                <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors font-light">
                                    Network Diagnostics
                                </a>
                            </li>
                        </ul>
                    </div>

                    {/* Resources */}
                    <div>
                        <h4 className="text-white font-semibold mb-6 text-sm uppercase tracking-wider">Resources</h4>
                        <ul className="space-y-3">
                            <li>
                                <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors font-light">
                                    Documentation
                                </a>
                            </li>
                            <li>
                                <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors font-light">
                                    API Reference
                                </a>
                            </li>
                            <li>
                                <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white text-sm transition-colors font-light">
                                    GitHub
                                </a>
                            </li>
                        </ul>
                    </div>

                    {/* Company */}
                    <div>
                        <h4 className="text-white font-semibold mb-6 text-sm uppercase tracking-wider">Company</h4>
                        <ul className="space-y-3">
                            <li>
                                <a href="#about" className="text-gray-400 hover:text-white text-sm transition-colors font-light">
                                    About Us
                                </a>
                            </li>
                            <li>
                                <a href="/chat" className="text-gray-400 hover:text-white text-sm transition-colors font-light">
                                    Try Demo
                                </a>
                            </li>
                            <li>
                                <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors font-light">
                                    Contact
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center">
                    <p className="text-gray-500 text-sm font-light">
                        © {currentYear} Telecom AI Assistant. All rights reserved.
                    </p>
                    <div className="flex space-x-8 mt-4 md:mt-0">
                        <a href="#" className="text-gray-500 hover:text-white text-sm transition-colors font-light">
                            Privacy Policy
                        </a>
                        <a href="#" className="text-gray-500 hover:text-white text-sm transition-colors font-light">
                            Terms of Service
                        </a>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
