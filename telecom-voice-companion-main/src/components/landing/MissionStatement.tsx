const MissionStatement = () => {
  return (
    <section className="section-padding bg-secondary">
      <div className="container-narrow px-6 text-center">
        <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-foreground mb-6 leading-relaxed">
          <span className="gradient-text">Born from frustration</span> with generic chatbots
        </h2>
        <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
          Generic chatbots fail when customers ask about specific plans, billing issues, 
          or network problems. Our AI is different—it's grounded in your actual 
          documentation with <span className="text-primary font-semibold">RAG technology</span>, 
          delivering real-time responses that actually help.
        </p>
        
        {/* Dual CTA for target audiences */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mt-10">
          <a href="#enterprise" className="inline-flex items-center gap-2 text-primary font-semibold hover:underline">
            For Telecom Companies →
          </a>
          <span className="hidden sm:block text-border">|</span>
          <a href="#developers" className="inline-flex items-center gap-2 text-primary font-semibold hover:underline">
            For Developers →
          </a>
        </div>
      </div>
    </section>
  );
};

export default MissionStatement;
