import { Bot, Mic, BarChart3, Wrench } from 'lucide-react';

const features = [
  {
    icon: Bot,
    title: 'RAG-Powered Intelligence',
    description: 'ChromaDB semantic search ensures accurate answers from your knowledge base with context-aware responses.',
  },
  {
    icon: Mic,
    title: 'Voice AI Integration',
    description: 'Real-time STT/TTS with Faster-Whisper and Kokoro for natural, human-like conversations.',
  },
  {
    icon: BarChart3,
    title: 'Real-Time Analytics',
    description: 'Track customer interactions, satisfaction scores, and resolution rates with actionable insights.',
  },
  {
    icon: Wrench,
    title: 'Automated Diagnostics',
    description: 'Function calling for plan queries, billing automation, and network troubleshooting.',
  },
];

const FeaturesGrid = () => {
  return (
    <section id="features" className="section-padding bg-background">
      <div className="container-wide px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Everything You Need for{' '}
            <span className="gradient-text">Intelligent Support</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            A complete solution designed specifically for the telecom industry
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="feature-card group"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="w-14 h-14 bg-primary/10 rounded-xl flex items-center justify-center mb-5 group-hover:bg-primary/20 transition-colors">
                <feature.icon className="w-7 h-7 text-primary" />
              </div>
              <h3 className="text-xl font-bold text-foreground mb-3">
                {feature.title}
              </h3>
              <p className="text-muted-foreground leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesGrid;
