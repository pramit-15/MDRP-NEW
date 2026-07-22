import { SignUp } from "@clerk/nextjs";
import { Activity, Sparkles } from "lucide-react";

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex">
      {/* Left Panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-emerald-600 to-blue-700 dark:from-emerald-900 dark:to-slate-900 flex-col justify-between p-12 relative overflow-hidden">
        <div className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: "radial-gradient(circle at 20% 50%, hsl(158 64% 52% / 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 20%, hsl(217 91% 60% / 0.3) 0%, transparent 50%)",
          }}
        />
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-16">
            <div className="h-10 w-10 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <span className="text-white font-bold text-xl tracking-tight">MDRP</span>
          </div>
          <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2 mb-6">
            <Sparkles className="h-4 w-4 text-amber-300" />
            <span className="text-white text-sm font-medium">Free to get started</span>
          </div>
          <h1 className="text-4xl font-bold text-white mb-4 leading-tight">
            Begin Your Health Intelligence Journey
          </h1>
          <p className="text-emerald-100 text-lg leading-relaxed mb-8">
            Create your account to access personalized disease risk assessments, 
            track your health over time, and get AI-powered insights.
          </p>
          <div className="space-y-3">
            {[
              "No credit card required",
              "Instant access to all predictions",
              "Secure, encrypted health data",
              "Complete prediction history",
            ].map((item) => (
              <div key={item} className="flex items-center gap-3">
                <div className="h-5 w-5 rounded-full bg-white/20 flex items-center justify-center shrink-0">
                  <svg className="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-emerald-100 text-sm">{item}</span>
              </div>
            ))}
          </div>
        </div>
        <p className="relative z-10 text-emerald-200 text-xs">
          Your health data is protected by Clerk's enterprise-grade security.
        </p>
      </div>

      {/* Right Panel */}
      <div className="flex-1 flex flex-col items-center justify-center p-8 bg-background">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-2 mb-8 justify-center">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-500 to-emerald-500 flex items-center justify-center">
              <Activity className="h-4 w-4 text-white" />
            </div>
            <span className="font-bold text-lg">MDRP</span>
          </div>
          <SignUp
            appearance={{
              elements: {
                rootBox: "w-full",
                card: "shadow-none border-0 bg-transparent p-0",
                headerTitle: "text-2xl font-bold text-foreground",
                headerSubtitle: "text-muted-foreground",
                socialButtonsBlockButton:
                  "border border-border bg-background hover:bg-muted text-foreground rounded-xl h-11 transition-colors",
                dividerLine: "bg-border",
                dividerText: "text-muted-foreground",
                formFieldLabel: "text-foreground font-medium",
                formFieldInput:
                  "border-input bg-background text-foreground rounded-xl h-11 focus:ring-2 focus:ring-blue-500",
                formButtonPrimary:
                  "bg-emerald-600 hover:bg-emerald-700 rounded-xl h-11 font-semibold transition-colors",
                footerActionLink: "text-blue-600 hover:text-blue-700",
              },
            }}
          />
        </div>
      </div>
    </div>
  );
}
