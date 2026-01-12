import Navbar from './Navbar';
import Hero from './Hero';
import Features from './Features';
import Capabilities from './Capabilities';
import Mission from './Mission';
import Footer from './Footer';

const LandingPage = () => {
    return (
        <div className="min-h-screen">
            <Navbar />
            <Hero />
            <Features />
            <Capabilities />
            <Mission />
            <Footer />
        </div>
    );
};

export default LandingPage;
