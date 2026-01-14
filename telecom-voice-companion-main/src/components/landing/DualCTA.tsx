import { Button } from '@/components/ui/button';
import { Building2, Code, Check, ArrowRight, Github } from 'lucide-react';

const DualCTA = () => {
  return (
    <section id="demo" className="section-padding bg-secondary">
      <div className="container-wide px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-lg text-muted-foreground">
            Choose the path that fits your needs
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {/* For Telecom Companies */}
          <div id="enterprise" className="cta-card-light">
            <div className="w-14 h-14 bg-primary/10 rounded-xl flex items-center justify-center mb-6">
              <Building2 className="w-7 h-7 text-primary" />
            </div>
            <h3 className="text-2xl md:text-3xl font-bold text-foreground mb-4">
              For Telecom Companies
            </h3>
            <p className="text-muted-foreground mb-6">
              Scale customer support, reduce costs by 60%, and provide 24/7 
              intelligent assistance to your customers.
            </p>
            <ul className="space-y-3 mb-8">
              {[
                'Enterprise-grade security and compliance',
                'Custom knowledge base integration',
                'White-label deployment options',
                'Dedicated support and SLA',
              ].map((item, i) => (
                <li key={i} className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                  <span className="text-foreground">{item}</span>
                </li>
              ))}
            </ul>
            <Button variant="hero" size="lg" className="w-full group">
              Request Enterprise Demo
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
          </div>

          {/* For Developers */}
          <div id="developers" className="cta-card-gradient">
            <div className="w-14 h-14 bg-primary-foreground/10 rounded-xl flex items-center justify-center mb-6">
              <Code className="w-7 h-7 text-primary-foreground" />
            </div>
            <h3 className="text-2xl md:text-3xl font-bold mb-4">
              For Developers
            </h3>
            <p className="text-primary-foreground/80 mb-6">
              Build with fully open-source technology. Customize every aspect, 
              deploy anywhere, and integrate with existing systems.
            </p>
            <ul className="space-y-3 mb-8">
              {[
                'Complete API access with FastAPI',
                'Docker-ready deployment',
                'Comprehensive documentation',
                'Active community support',
              ].map((item, i) => (
                <li key={i} className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-primary-foreground/80 flex-shrink-0 mt-0.5" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
            <Button variant="heroInverse" size="lg" className="w-full group">
              <Github className="mr-2 w-5 h-5" />
              Explore GitHub Repo
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default DualCTA;
