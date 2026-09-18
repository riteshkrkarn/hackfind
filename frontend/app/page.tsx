import { ClosingCta } from "@/components/landing/ClosingCta";
import { Hero } from "@/components/landing/Hero";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { LandingHeader } from "@/components/landing/LandingHeader";

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <LandingHeader />
      <main>
        <Hero />
        <HowItWorks />
        <ClosingCta />
      </main>
    </div>
  );
}
