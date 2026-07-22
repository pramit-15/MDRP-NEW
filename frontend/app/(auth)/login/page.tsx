import { SignIn } from "@clerk/nextjs";
import { Activity } from "lucide-react";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex">
      {/* Left Panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 to-blue-800 dark:from-blue-900 dark:to-slate-900 flex-col justify-between p-12 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-mesh opacity-40" />
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-16">
            <div className="h-10 w-10 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <span className="text-white font-bold text-xl tracking-tight">MDRP</span>
          </div>
          <h1 className="text-4xl font-bold text-white mb-4 leading-tight">
            Your Health Intelligence Platform
          </h1>
          <p className="text-blue-100 text-lg leading-relaxed mb-8">
            Access AI-powered disease risk predictions powered by clinical ML models 
            and explainable AI insights.
          </p>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: "Disease Models", value: "4" },
              { label: "Clinical Markers", value: "40+" },
              { label: "AI Methods", value: "ML+Clinical" },
              { label: "Privacy", value: "Clerk Secured" },
            ].map((stat) => (
              <div key={stat.label} className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                <div className="text-2xl font-bold text-white">{stat.value}</div>
                <div className="text-blue-200 text-sm">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
        <p className="relative z-10 text-blue-200 text-xs">
          For educational purposes only. Not a substitute for medical advice.
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
          <SignIn
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
                  "bg-blue-600 hover:bg-blue-700 rounded-xl h-11 font-semibold transition-colors",
                footerActionLink: "text-blue-600 hover:text-blue-700",
                identityPreviewEditButton: "text-blue-600",
                formResendCodeLink: "text-blue-600",
                otpCodeFieldInput:
                  "border-input bg-background rounded-xl text-foreground",
              },
            }}
          />
        </div>
      </div>
    </div>
  );
}
