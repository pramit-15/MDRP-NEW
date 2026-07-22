import Link from "next/link";
import { Heart, Brain, Activity, ArrowRight, Shield, Zap, BarChart3, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const features = [
  {
    icon: Heart,
    title: "Heart Disease Risk",
    description: "Assess cardiovascular risk using 13+ clinical markers including ECG patterns, cholesterol levels, and blood pressure.",
    color: "text-red-500",
    bg: "bg-red-500/10",
  },
  {
    icon: Activity,
    title: "Diabetes Risk",
    description: "Predict diabetes probability using HbA1c, fasting glucose, insulin levels, and metabolic indicators.",
    color: "text-amber-500",
    bg: "bg-amber-500/10",
  },
  {
    icon: Brain,
    title: "Kidney Disease Risk",
    description: "Evaluate renal health through creatinine, eGFR, blood urea, electrolytes, and clinical symptoms.",
    color: "text-blue-500",
    bg: "bg-blue-500/10",
  },
];

const benefits = [
  "ML + Clinical risk scoring (blended ensemble)",
  "SHAP-powered explainability",
  "PDF lab report parsing with AI",
  "Complete prediction history",
  "Export & share results",
  "Dark mode & mobile-ready",
];

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-500 to-emerald-500 flex items-center justify-center">
              <Activity className="h-4 w-4 text-white" />
            </div>
            <span className="font-bold text-lg tracking-tight">MDRP</span>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="sm">Sign In</Button>
            </Link>
            <Link href="/register">
              <Button size="sm">Get Started</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="container pt-24 pb-20 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-4 py-1.5 text-sm text-blue-700 dark:border-blue-800/50 dark:bg-blue-900/20 dark:text-blue-400 mb-8">
          <Shield className="h-3.5 w-3.5" />
          <span>AI-Powered Health Risk Assessment</span>
        </div>

        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight mb-6 leading-tight">
          Know Your{" "}
          <span className="gradient-text">Health Risks</span>
          <br />
          Before They Know You
        </h1>

        <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
          Predict your risk for heart disease, diabetes, and kidney disease using advanced machine learning 
          combined with clinical scoring — all from a single blood test panel.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
          <Link href="/register">
            <Button size="xl" className="group">
              Start Free Assessment
              <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Button>
          </Link>
          <Link href="/login">
            <Button size="xl" variant="outline">
              View Demo Dashboard
            </Button>
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-8 max-w-lg mx-auto">
          {[
            { value: "4", label: "Disease Models" },
            { value: "40+", label: "Clinical Markers" },
            { value: "AI", label: "PDF Parsing" },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-3xl font-bold text-blue-600">{stat.value}</div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="container pb-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-3">Comprehensive Disease Risk Analysis</h2>
          <p className="text-muted-foreground">Three specialized ML models, one unified platform</p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="group rounded-2xl border border-border/50 bg-card p-8 hover:shadow-xl hover:-translate-y-1 transition-all duration-300"
            >
              <div className={`inline-flex h-12 w-12 items-center justify-center rounded-xl ${feature.bg} mb-5`}>
                <feature.icon className={`h-6 w-6 ${feature.color}`} />
              </div>
              <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
              <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Benefits */}
      <section className="container pb-20">
        <div className="rounded-2xl bg-gradient-to-br from-blue-600/10 to-emerald-500/10 border border-blue-200/50 dark:border-blue-800/30 p-12">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <Badge variant="default" className="mb-4">Everything Included</Badge>
              <h2 className="text-3xl font-bold mb-4">
                Professional-Grade Health Intelligence
              </h2>
              <p className="text-muted-foreground mb-6 leading-relaxed">
                Built on production ML models trained on clinical datasets. Every prediction 
                is transparent, explainable, and backed by both machine learning and clinical risk scoring.
              </p>
              <Link href="/register">
                <Button className="group">
                  Get Started Free
                  <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </div>
            <div className="grid grid-cols-1 gap-3">
              {benefits.map((benefit) => (
                <div key={benefit} className="flex items-center gap-3">
                  <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" />
                  <span className="text-sm font-medium">{benefit}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="container pb-24">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-3">How It Works</h2>
          <p className="text-muted-foreground">Get your risk assessment in 3 simple steps</p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { step: "01", icon: Zap, title: "Enter Your Data", desc: "Input lab values manually or upload a PDF report for automatic extraction." },
            { step: "02", icon: Brain, title: "AI Analysis", desc: "Our ensemble model combines ML predictions with clinical risk scoring algorithms." },
            { step: "03", icon: BarChart3, title: "Get Insights", desc: "Receive detailed risk scores, visual breakdowns, and personalized recommendations." },
          ].map((item) => (
            <div key={item.step} className="text-center">
              <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-600/10 mb-5">
                <item.icon className="h-7 w-7 text-blue-600" />
              </div>
              <div className="text-xs font-bold text-blue-600 mb-2 tracking-widest uppercase">{item.step}</div>
              <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-muted/30 py-8">
        <div className="container flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 rounded bg-gradient-to-br from-blue-500 to-emerald-500 flex items-center justify-center">
              <Activity className="h-3 w-3 text-white" />
            </div>
            <span className="font-semibold text-sm">MDRP</span>
          </div>
          <p className="text-xs text-muted-foreground">
            © 2026 Multi Disease Risk Prediction Platform. For educational and informational purposes only.
          </p>
          <p className="text-xs text-muted-foreground">
            Not a substitute for professional medical advice.
          </p>
        </div>
      </footer>
    </main>
  );
}
