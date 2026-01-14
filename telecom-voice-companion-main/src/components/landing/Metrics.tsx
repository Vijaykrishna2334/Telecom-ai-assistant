import { Zap, CheckCircle, Rocket, MessageCircle } from 'lucide-react';

const metrics = [
  { icon: Zap, value: '<2s', label: 'Response Time' },
  { icon: CheckCircle, value: '95%+', label: 'Accuracy with RAG' },
  { icon: Rocket, value: '99.9%', label: 'Uptime SLA' },
  { icon: MessageCircle, value: '10K+', label: 'Conversations Handled' },
];

const Metrics = () => {
  return (
    <section className="py-16 bg-gradient-metrics">
      <div className="container-wide px-6">
        <div className="grid md:grid-cols-4 gap-8 text-center">
          {metrics.map((metric, index) => (
            <div key={index} className="text-primary-foreground">
              <div className="flex justify-center mb-3">
                <metric.icon className="w-8 h-8 opacity-80" />
              </div>
              <div className="text-4xl md:text-5xl font-bold mb-2">{metric.value}</div>
              <div className="text-primary-foreground/80">{metric.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Metrics;
