import { motion } from "framer-motion";
import { Activity, ArrowRight, Brain, HeartPulse, ShieldCheck, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const features = [
  {
    title: "Patient journey intelligence",
    description: "Timeline-driven insight into adherence, missed visits, and engagement signals.",
    icon: HeartPulse,
  },
  {
    title: "AI risk operations",
    description: "Predictive dropout scoring with explainable drivers and cohort analytics.",
    icon: Brain,
  },
  {
    title: "Intervention automation",
    description: "Queued outreach workflows, delivery retries, and impact tracking.",
    icon: Sparkles,
  },
  {
    title: "Executive dashboards",
    description: "Clinic-wide KPIs, segmentation, funnels, and performance views.",
    icon: Activity,
  },
];

const workflowSteps = [
  "Ingest clinical signals and behavior history",
  "Generate risk predictions with explainability",
  "Trigger intervention queue and delivery simulation",
  "Measure engagement, adherence, and outcomes",
];

export function LandingPage() {
  return (
    <div className="relative overflow-hidden font-display">
      <div className="absolute -top-40 right-[-10%] h-80 w-80 rounded-full bg-teal-300/40 blur-3xl dark:bg-teal-700/30" />
      <div className="absolute top-24 left-[-15%] h-96 w-96 rounded-full bg-cyan-200/50 blur-3xl dark:bg-cyan-900/30" />

      <div className="relative mx-auto max-w-6xl space-y-20 px-6 pb-24 pt-16 lg:px-8">
        <section className="grid gap-12 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-card/80 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-primary">
              Clinical operations intelligence
            </div>
            <h1 className="text-balance text-4xl font-semibold leading-tight md:text-5xl">
              DentalAI brings predictive intelligence to every patient journey.
            </h1>
            <p className="text-lg text-muted-foreground">
              Operational AI for dental clinics: risk scoring, automated interventions, and executive
              analytics designed for production-grade care delivery.
            </p>
            <div className="flex flex-wrap gap-3">
              <Button asChild className="rounded-full px-6">
                <Link to="/login">
                  Request demo
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button asChild variant="outline" className="rounded-full px-6">
                <Link to="/register">Explore the platform</Link>
              </Button>
            </div>
            <div className="flex flex-wrap gap-6 text-sm text-muted-foreground">
              <span>AI readiness: production workflows</span>
              <span>Research-backed methodology</span>
              <span>Deployment-grade architecture</span>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {[
              { label: "Adherence lift", value: "18%" },
              { label: "Intervention SLA", value: "< 2h" },
              { label: "Prediction coverage", value: "100%" },
              { label: "Workflow automation", value: "Daily" },
            ].map((stat) => (
              <Card key={stat.label} className="">
                <CardContent className="space-y-2 p-5">
                  <p className="text-xs uppercase tracking-wider text-muted-foreground">
                    {stat.label}
                  </p>
                  <p className="text-3xl font-semibold">{stat.value}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-4">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.05 }}
            >
              <Card className="">
                <CardHeader className="space-y-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
                    <feature.icon className="h-5 w-5 text-primary" />
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                  <CardDescription className="text-sm text-muted-foreground">
                    {feature.description}
                  </CardDescription>
                </CardHeader>
              </Card>
            </motion.div>
          ))}
        </section>

        <section className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
          <div className="space-y-4">
            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-primary">
              AI workflow
            </p>
            <h2 className="text-3xl font-semibold">Operational AI, end-to-end</h2>
            <p className="text-muted-foreground">
              DentalAI orchestrates prediction, intervention, and analytics flows with clear
              accountability across clinical teams.
            </p>
            <div className="space-y-3">
              {workflowSteps.map((step, index) => (
                <div key={step} className="flex items-start gap-3">
                  <div className="mt-1 flex h-6 w-6 items-center justify-center rounded-full bg-primary/15 text-xs font-semibold text-primary">
                    {index + 1}
                  </div>
                  <p className="text-sm text-muted-foreground">{step}</p>
                </div>
              ))}
            </div>
          </div>

          <Card className="">
            <CardHeader>
              <CardTitle className="text-lg">Analytics preview</CardTitle>
              <CardDescription>Executive KPIs in a single glance</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-3 gap-3">
                {[
                  { label: "Low", value: 42 },
                  { label: "Medium", value: 28 },
                  { label: "High", value: 12 },
                ].map((item) => (
                  <div key={item.label} className="rounded-xl border border-border/50 bg-card/70 p-3 text-center">
                    <p className="text-xs text-muted-foreground">{item.label}</p>
                    <p className="mt-1 text-lg font-semibold">{item.value}%</p>
                  </div>
                ))}
              </div>
              <div className="space-y-2">
                {[0.72, 0.6, 0.48, 0.38].map((value, index) => (
                  <div key={index} className="h-3 w-full overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-primary to-teal-400"
                      style={{ width: `${value * 100}%` }}
                    />
                  </div>
                ))}
              </div>
              <div className="rounded-xl border border-border/50 bg-card/70 p-3 text-sm text-muted-foreground">
                Automated insights refresh every 30 minutes and trigger threshold alerts.
              </div>
            </CardContent>
          </Card>
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <Card className="">
            <CardHeader>
              <CardTitle className="text-lg">Production readiness</CardTitle>
              <CardDescription>Deployment-first architecture</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              {[
                "Health endpoints for live and ready checks",
                "Celery beat automation schedules",
                "Production env templates and scripts",
                "RBAC enforcement across APIs",
              ].map((item) => (
                <div key={item} className="flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-primary" />
                  <span>{item}</span>
                </div>
              ))}
            </CardContent>
          </Card>

          <div className="space-y-4">
            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-primary">
              Showcase ready
            </p>
            <h2 className="text-3xl font-semibold">Tell a complete story in minutes.</h2>
            <p className="text-muted-foreground">
              Walkthrough-ready dashboards, patient journeys, and intervention outcomes are designed
              for demos, portfolios, and research presentations.
            </p>
            <Button asChild variant="outline" className="rounded-full">
              <Link to="/login">Open live demo</Link>
            </Button>
          </div>
        </section>

        <section className="rounded-3xl border border-border/60 bg-card/80 p-8 text-center ">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-primary">DentalAI</p>
          <h2 className="mt-3 text-3xl font-semibold">Ready for production-grade care intelligence</h2>
          <p className="mx-auto mt-3 max-w-2xl text-muted-foreground">
            Deploy a modern AI operations layer that aligns clinicians, administrators, and patients
            around a measurable adherence journey.
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <Button asChild className="rounded-full px-6">
              <Link to="/register">Start a showcase</Link>
            </Button>
            <Button asChild variant="outline" className="rounded-full px-6">
              <Link to="/login">Review dashboards</Link>
            </Button>
          </div>
        </section>
      </div>
    </div>
  );
}
