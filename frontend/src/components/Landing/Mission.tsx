const Mission = () => {
    return (
        <section id="about" className="section bg-[#FBFAF9] relative overflow-hidden">
            {/* Ghost text background */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-5">
                <h3 className="text-9xl font-serif font-bold text-gray-900 select-none">
                    AI
                </h3>
            </div>

            <div className="container relative z-10">
                <div className="max-w-4xl mx-auto text-center">
                    <h3 className="text-4xl md:text-6xl font-serif font-light text-gray-900 mb-6">
                        Join the Telecom AI Community
                    </h3>
                    <p className="text-lg text-gray-700 leading-relaxed mb-8 font-light">
                        Ready to redefine the boundaries of telecom customer service? Join Telecom AI today and be part of the
                        community that's setting the tone for tomorrow's AI innovations. Where will your imagination take you?
                        Let Telecom AI be the launchpad for your voice AI journey.
                    </p>
                    <p className="text-lg text-gray-700 leading-relaxed mb-12 font-light">
                        Experience a future where telecom is more accessible, intuitive, and conversational.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <button
                            onClick={() => window.location.href = '/chat'}
                            className="group px-10 py-4 bg-gray-900 text-white font-semibold rounded-full hover:bg-gray-800 transition-all inline-flex items-center justify-center space-x-2"
                        >
                            <span>START FOR FREE</span>
                            <span className="group-hover:translate-x-1 transition-transform">→</span>
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default Mission;
