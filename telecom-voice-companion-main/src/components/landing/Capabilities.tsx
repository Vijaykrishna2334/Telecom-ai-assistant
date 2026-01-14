import { 
  Smartphone, 
  DollarSign, 
  Wifi, 
  Mic2, 
  Globe2, 
  RefreshCw, 
  TrendingUp, 
  Shield 
} from 'lucide-react';

const capabilities = [
  { 
    icon: Smartphone, 
    title: 'Plan Recommendations', 
    desc: 'AI suggests best plans based on usage patterns' 
  },
  { 
    icon: DollarSign, 
    title: 'Billing Inquiries', 
    desc: 'Instant invoice and payment status' 
  },
  { 
    icon: Wifi, 
    title: 'Network Diagnostics', 
    desc: 'Speed tests and coverage analysis' 
  },
  { 
    icon: Mic2, 
    title: 'Voice Conversations', 
    desc: 'Natural speech interaction' 
  },
  { 
    icon: Globe2, 
    title: 'Multi-Language', 
    desc: 'Regional language support' 
  },
  { 
    icon: RefreshCw, 
    title: 'Human Escalation', 
    desc: 'Seamless agent handoff' 
  },
  { 
    icon: TrendingUp, 
    title: 'Usage Analytics', 
    desc: 'Customer behavior insights' 
  },
  { 
    icon: Shield, 
    title: 'Enterprise Security', 
    desc: 'SOC2 compliance ready' 
  },
];

const Capabilities = () => {
  return (
    <section id="capabilities" className="section-padding bg-background">
      <div className="container-wide px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            <span className="gradient-text">Powerful</span> Capabilities
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Everything you need to deliver exceptional telecom customer support
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
          {capabilities.map((cap, index) => (
            <div
              key={index}
              className="capability-card group"
            >
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-accent/20 transition-colors">
                <cap.icon className="w-6 h-6 text-accent" />
              </div>
              <h4 className="font-bold text-foreground mb-1">{cap.title}</h4>
              <p className="text-sm text-muted-foreground">{cap.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Capabilities;
