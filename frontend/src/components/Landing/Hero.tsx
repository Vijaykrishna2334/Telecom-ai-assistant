const Hero = () => {
    return (
        <section className="min-h-screen flex items-center justify-center pt-20 px-4 relative overflow-hidden bg-black">
            {/* Subtle grid pattern */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px]"></div>

            {/* Animated gradient orbs */}
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse-slow"></div>
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }}></div>

            <div className="container mx-auto relative z-10">
                <div className="text-center max-w-5xl mx-auto">
                    {/* Main Headline - Using Serif-like styling */}
                    <h1 className="text-5xl md:text-7xl lg:text-8xl font-serif font-light text-white mb-8 leading-tight tracking-tight">
                        Your Custom{' '}
                        <span className="block mt-2">
                            <span className="italic">Telecom AI</span> Assistant
                        </span>
                    </h1>

                    {/* Subheadline */}
                    <p className="text-lg md:text-xl text-gray-400 mb-12 max-w-3xl mx-auto font-light">
                        Build AI-Powered Customer Support, Deploy Voice & Chat on Any Platform
                    </p>

                    {/* CTA Button */}
                    <div className="mb-16">
                        <button
                            onClick={() => window.location.href = '/chat'}
                            className="group px-8 py-3 bg-white text-black font-semibold rounded-full hover:bg-gray-200 transition-all inline-flex items-center space-x-3 text-lg"
                        >
                            <span>START FOR FREE</span>
                            <span className="group-hover:translate-x-1 transition-transform">→</span>
                        </button>
                    </div>

                    {/* Partner Logos / Integration Pills */}
                    <div className="flex flex-wrap gap-4 justify-center items-center text-sm opacity-50">
                        <div className="px-6 py-2 border border-white/20 rounded-full text-gray-400">
                            Speech-to-Text
                        </div>
                        <div className="px-6 py-2 border border-white/20 rounded-full text-gray-400">
                            Text-to-Speech
                        </div>
                        <div className="px-6 py-2 border border-white/20 rounded-full text-gray-400">
                            RAG Powered
                        </div>
                        <div className="px-6 py-2 border border-white/20 rounded-full text-gray-400">
                            Real-Time Voice
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default Hero;
