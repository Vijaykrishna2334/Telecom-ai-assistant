import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Play, BookOpen } from 'lucide-react';
import VoiceWaveVideo from './VoiceWaveVideo';
const Hero = () => {
  return <section className="relative min-h-screen flex items-center bg-gradient-hero overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 -left-20 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 -right-20 w-96 h-96 bg-accent/5 rounded-full blur-3xl" />
      </div>

      <div className="container-wide px-6 pt-32 pb-20 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full text-primary text-sm font-medium mb-8 animate-fade-in">
            <span className="w-2 h-2 bg-accent rounded-full animate-pulse" />
            AI-Powered Telecom Support
          </div>

          {/* Main Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-foreground mb-6 leading-tight animate-fade-in" style={{
          animationDelay: '0.1s'
        }}>
            AI That Actually
            <br />
            <span className="gradient-text">Understands Humans</span>
          </h1>

          {/* Subheading */}
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-10 animate-fade-in" style={{
          animationDelay: '0.2s'
        }}>
            Deploy intelligent customer support in minutes with RAG-powered voice AI
            trained on your knowledge base. Reduce costs, improve satisfaction.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in" style={{
          animationDelay: '0.3s'
        }}>
            <Link to="/auth">
              <Button variant="hero" size="lg" className="group">
                <Play className="mr-2 h-5 w-5 group-hover:scale-110 transition-transform" />
                Try Live Demo
              </Button>
            </Link>
            <Button variant="outline" size="lg" className="group">
              <BookOpen className="mr-2 h-5 w-5" />
              View Documentation
            </Button>
          </div>

          {/* Reference-matched waveform (cropped video fallback) */}
          <div className="mt-16 animate-fade-in-up" style={{
          animationDelay: '0.4s'
        }}>
            <VoiceWaveVideo />
          </div>
        </div>
      </div>
    </section>;
};
export default Hero;