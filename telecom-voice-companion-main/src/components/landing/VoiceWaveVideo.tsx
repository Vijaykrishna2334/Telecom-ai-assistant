import waveAnimation from '@/assets/Untitled video - Made with Clipchamp (1) (1).mp4';

const VoiceWaveVideo = () => {
  return (
    <div className="relative w-full max-w-5xl mx-auto">
      {/* Container clips to show only the center waveform, removing black bars */}
      <div className="relative rounded-[2rem] overflow-hidden shadow-2xl bg-[#0a0a0a]">
        <div className="relative w-full h-[180px] sm:h-[220px] md:h-[280px] lg:h-[320px] overflow-hidden">
          <video
            className="absolute left-1/2 top-1/2 w-full max-w-none object-cover"
            style={{
              transform: 'translate(-50%, -50%) scale(1.4)',
            }}
            src={waveAnimation}
            autoPlay
            loop
            muted
            playsInline
            preload="auto"
            aria-label="Animated voice waveform"
          />
        </div>

        {/* Edge fades for seamless blending */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute left-0 top-0 bottom-0 w-16 bg-gradient-to-r from-[#0a0a0a] to-transparent" />
          <div className="absolute right-0 top-0 bottom-0 w-16 bg-gradient-to-l from-[#0a0a0a] to-transparent" />
        </div>
      </div>
    </div>
  );
};

export default VoiceWaveVideo;

