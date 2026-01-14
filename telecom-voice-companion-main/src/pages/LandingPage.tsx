import Navbar from '@/components/landing/Navbar';
import Hero from '@/components/landing/Hero';
import MissionStatement from '@/components/landing/MissionStatement';
import FeaturesGrid from '@/components/landing/FeaturesGrid';
import TechStack from '@/components/landing/TechStack';
import Capabilities from '@/components/landing/Capabilities';
import Metrics from '@/components/landing/Metrics';
import DualCTA from '@/components/landing/DualCTA';
import Footer from '@/components/landing/Footer';

const LandingPage = () => {
  return (
    <div className="min-h-screen">
      <Navbar />
      <Hero />
      <MissionStatement />
      <FeaturesGrid />
      <TechStack />
      <Capabilities />
      <Metrics />
      <DualCTA />
      <Footer />
    </div>
  );
};

export default LandingPage;
