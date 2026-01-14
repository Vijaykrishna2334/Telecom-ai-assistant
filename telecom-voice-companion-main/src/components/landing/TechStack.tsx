const technologies = [
  { name: 'FastAPI', category: 'Backend', icon: '⚡' },
  { name: 'React', category: 'Frontend', icon: '⚛️' },
  { name: 'Ollama', category: 'LLM Runtime', icon: '🦙' },
  { name: 'ChromaDB', category: 'Vector DB', icon: '🔍' },
  { name: 'PostgreSQL', category: 'Database', icon: '🐘' },
  { name: 'Redis', category: 'Cache', icon: '🔴' },
  { name: 'Docker', category: 'DevOps', icon: '🐳' },
  { name: 'WebSocket', category: 'Real-time', icon: '🔌' },
];

const TechStack = () => {
  return (
    <section id="technology" className="section-padding bg-secondary">
      <div className="container-wide px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Built with{' '}
            <span className="gradient-text">Modern Tech</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Production-ready architecture using best-in-class open-source technologies
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
          {technologies.map((tech, index) => (
            <div
              key={index}
              className="tech-badge group cursor-default"
            >
              <div className="text-3xl mb-3 group-hover:scale-110 transition-transform">
                {tech.icon}
              </div>
              <div className="font-bold text-foreground mb-1">{tech.name}</div>
              <div className="text-sm text-muted-foreground">{tech.category}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default TechStack;
