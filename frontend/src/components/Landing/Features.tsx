const Features = () => {
    const features = [
        {
            icon: '🗣️',
            title: 'Human-Like Interaction',
            description:
                'Create organic voice AI experiences with instant response times, emotional recognition, and natural conversation flows.',
        },
        {
            icon: '🔓',
            title: 'Open Source & Unlimited',
            description:
                'Built on open-source Voice SDK. For developers and enterprises - get started instantly with full customization capabilities.',
        },
        {
            icon: '🎨',
            title: 'Customize Like Never Before',
            description:
                'Build AI personalities that are vibrant and interactive. Customize voice, conversation style, tone, and capabilities—no coding required!',
        },
        {
            icon: '💚',
            title: 'Empathy & Understanding',
            description:
                'Our AI doesn\'t just understand commands; it interprets emotions and generates empathic responses for natural communication.',
        },
    ];

    return (
        <section id="features" className="section bg-gray-50">
            <div className="container">
                <div className="text-center mb-16">
                    <h2 className="text-4xl md:text-6xl font-serif font-light text-gray-900 mb-4">
                        Build Your Ideal Customer Support Experience
                    </h2>
                    <p className="text-xl text-gray-600 max-w-3xl mx-auto font-light">
                        Empower your telecom business with seamless AI-driven dialogue
                    </p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {features.map((feature, index) => (
                        <div
                            key={index}
                            className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-lg transition-shadow duration-300 border border-gray-100"
                        >
                            <div className="text-5xl mb-4">
                                {feature.icon}
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-3">
                                {feature.title}
                            </h3>
                            <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default Features;
