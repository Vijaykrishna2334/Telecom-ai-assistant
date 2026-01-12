const Capabilities = () => {
    const apiSection = {
        title: 'Powerful APIs for Developers & Enterprises',
        description:
            'Easy to use, powerful tools for complex tasks. Our platform includes comprehensive APIs for speech-to-text, text-to-speech, and language understanding. Whether it\'s for customer support or creating autonomous agents, Telecom AI is the trusted choice for developers looking to push the boundaries of what voice AI can do.',
    };

    const capabilities = [
        { icon: '🌐', title: 'Instant Translation', color: 'bg-blue-500' },
        { icon: '😊', title: 'Emotion Detection', color: 'bg-yellow-500' },
        { icon: '📅', title: 'Plan Management', color: 'bg-green-500' },
        { icon: '📱', title: 'Network Diagnostics', color: 'bg-red-500' },
        { icon: '💬', title: 'Natural Conversations', color: 'bg-purple-500' },
        { icon: '📚', title: 'Knowledge Integration', color: 'bg-cyan-500' },
        { icon: '🎯', title: 'Personality Builder', color: 'bg-pink-500' },
    ];

    return (
        <>
            {/* Powerful APIs Section */}
            <section className="section bg-black">
                <div className="container">
                    <div className="max-w-4xl mx-auto text-center">
                        <h2 className="text-4xl md:text-6xl font-serif font-light text-white mb-6">
                            {apiSection.title}
                        </h2>
                        <p className="text-lg text-gray-400 leading-relaxed mb-12 font-light">
                            {apiSection.description}
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <button
                                onClick={() => window.location.href = '/chat'}
                                className="px-8 py-3 bg-white text-black font-semibold rounded-full hover:bg-gray-200 transition-all"
                            >
                                Try a Demo
                            </button>
                            <button
                                onClick={() => window.location.href = '/chat'}
                                className="px-8 py-3 border border-white/20 text-white font-semibold rounded-full hover:bg-white/10 transition-all"
                            >
                                Explore Ecosystem
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            {/* Powerful Capabilities Section */}
            <section id="capabilities" className="section bg-gray-50">
                <div className="container">
                    <div className="max-w-4xl mx-auto">
                        <div className="mb-12">
                            <h2 className="text-4xl md:text-6xl font-serif font-light text-gray-900 mb-4">
                                Powerful Capabilities
                            </h2>
                            <p className="text-xl text-gray-600 font-light">
                                With advanced features supporting a wide range of applications—from customer support to plan recommendations—Telecom AI sets the stage for a future where AI is seamlessly integrated into everyday life.
                            </p>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                            {capabilities.map((capability, index) => (
                                <div
                                    key={index}
                                    className="group cursor-pointer"
                                >
                                    <div className="bg-white rounded-2xl p-6 border border-gray-200 hover:shadow-lg transition-all duration-300 flex flex-col items-center text-center space-y-3">
                                        <div className={`w-14 h-14 ${capability.color} rounded-xl flex items-center justify-center text-2xl`}>
                                            {capability.icon}
                                        </div>
                                        <h4 className="text-sm font-medium text-gray-900">
                                            {capability.title}
                                        </h4>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="mt-12 text-center">
                            <button
                                onClick={() => window.location.href = '/chat'}
                                className="px-8 py-3 bg-gray-900 text-white font-semibold rounded-full hover:bg-gray-800 transition-all"
                            >
                                Explore Capabilities
                            </button>
                        </div>
                    </div>
                </div>
            </section>
        </>
    );
};

export default Capabilities;
