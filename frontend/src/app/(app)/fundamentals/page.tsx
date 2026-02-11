"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const dimensions = [
  {
    name: "Architecture",
    color: "#06B6D4",
    description:
      "Business structure, processes, and systems. How the organization is built and how its parts connect.",
  },
  {
    name: "Design",
    color: "#A855F7",
    description:
      "User experience, interfaces, and workflows. How people interact with products, services, and each other.",
  },
  {
    name: "Engineering",
    color: "#F59E0B",
    description:
      "Technical implementation, infrastructure, and data. How solutions are built, deployed, and maintained.",
  },
];

const phases = [
  {
    name: "Generate",
    color: "#22C55E",
    description: "Ideation and initial exploration of possibilities.",
  },
  {
    name: "Review",
    color: "#F97316",
    description: "Critical analysis and refinement of generated ideas.",
  },
  {
    name: "Validate",
    color: "#3B82F6",
    description: "Testing, verification, and evidence-based confirmation.",
  },
  {
    name: "Summarize",
    color: "#8B5CF6",
    description: "Synthesis, documentation, and actionable conclusions.",
  },
];

const perspectiveGrid: Record<string, Record<string, string>> = {
  Architecture: {
    Generate: "Structure Discovery",
    Review: "Process Audit",
    Validate: "System Verification",
    Summarize: "Architecture Blueprint",
  },
  Design: {
    Generate: "Experience Ideation",
    Review: "Usability Critique",
    Validate: "Design Testing",
    Summarize: "Design Specification",
  },
  Engineering: {
    Generate: "Technical Exploration",
    Review: "Code Review",
    Validate: "Integration Testing",
    Summarize: "Technical Documentation",
  },
};

const agents = [
  {
    name: "Lyra",
    role: "Architecture Analyst",
    color: "#A855F7",
    description:
      "Analyzes business structures and organizational patterns to identify strengths and transformation opportunities.",
  },
  {
    name: "Mira",
    role: "Design Strategist",
    color: "#EC4899",
    description:
      "Evaluates user experiences and interface design, ensuring solutions are human-centered and intuitive.",
  },
  {
    name: "Dex",
    role: "Engineering Architect",
    color: "#3B82F6",
    description:
      "Assesses technical feasibility, infrastructure needs, and implementation pathways for proposed solutions.",
  },
  {
    name: "Rex",
    role: "Review Specialist",
    color: "#06B6D4",
    description:
      "Performs deep critical analysis, identifying gaps, risks, and areas requiring further examination.",
  },
  {
    name: "Vela",
    role: "Validation Expert",
    color: "#EAB308",
    description:
      "Tests assumptions against evidence, ensuring claims are substantiated and solutions are viable.",
  },
  {
    name: "Koda",
    role: "Documentation Synthesizer",
    color: "#22C55E",
    description:
      "Transforms findings into clear, actionable documentation and executive summaries.",
  },
  {
    name: "Halo",
    role: "Integration Specialist",
    color: "#F97316",
    description:
      "Ensures all dimensions work together cohesively, identifying cross-cutting concerns and dependencies.",
  },
  {
    name: "Nova",
    role: "Innovation Catalyst",
    color: "#EF4444",
    description:
      "Pushes boundaries with creative solutions, challenging conventional thinking to find breakthrough approaches.",
  },
];

const axiom = {
  name: "Axiom",
  role: "Adversarial Challenger",
  color: "#94A3B8",
  description:
    "The devil's advocate. Axiom challenges every conclusion from the specialist agents using bounded single-pass debate (max 3 LLM calls), ensuring nothing passes without rigorous scrutiny.",
};

const bankingStages = [
  {
    stage: "Bankable",
    icon: "1",
    description:
      "Raw perspective output from agent analysis, ready to be reviewed and curated.",
  },
  {
    stage: "Film",
    icon: "2",
    description:
      "Curated and refined output with decision audit trail attached. A snapshot of validated work.",
  },
  {
    stage: "Film Reel",
    icon: "3",
    description:
      "Collection of related films across perspectives, forming a complete narrative of the transformation journey.",
  },
  {
    stage: "Published VDBA",
    icon: "4",
    description:
      "The final deliverable — a Validated Digital Business Assessment, exportable as PDF or DOCX.",
  },
];

export default function FundamentalsPage() {
  return (
    <div className="p-6 md:p-8 space-y-12 max-w-6xl mx-auto">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          InCube Methodology
        </h1>
        <p className="mt-2 text-muted-foreground text-lg">
          Understanding the business transformation framework
        </p>
      </div>

      {/* Section 1: The 3 Dimensions */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">The 3 Dimensions</h2>
        <p className="text-muted-foreground">
          Every business challenge is examined through three complementary
          lenses, ensuring a holistic understanding of the problem space.
        </p>
        <div className="grid gap-4 md:grid-cols-3">
          {dimensions.map((dim) => (
            <Card key={dim.name}>
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <div
                    className="h-4 w-4 rounded-full"
                    style={{ backgroundColor: dim.color }}
                  />
                  <CardTitle className="text-lg">{dim.name}</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {dim.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Section 2: The 4 Phases */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">The 4 Phases</h2>
        <p className="text-muted-foreground">
          Each dimension progresses through four analytical phases, moving from
          exploration to synthesis.
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {phases.map((phase) => (
            <Card key={phase.name}>
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <Badge
                    variant="outline"
                    style={{ borderColor: phase.color, color: phase.color }}
                  >
                    {phase.name}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {phase.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Section 3: The 12 Perspectives */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">The 12 Perspectives</h2>
        <p className="text-muted-foreground">
          Each dimension intersects with each phase, creating 12 unique
          analytical perspectives that together form the complete InCube
          assessment.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr>
                <th className="p-2 text-left text-sm font-medium text-muted-foreground" />
                {phases.map((phase) => (
                  <th
                    key={phase.name}
                    className="p-2 text-center text-sm font-semibold"
                    style={{ color: phase.color }}
                  >
                    {phase.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {dimensions.map((dim) => (
                <tr key={dim.name}>
                  <td
                    className="p-2 text-sm font-semibold whitespace-nowrap"
                    style={{ color: dim.color }}
                  >
                    {dim.name}
                  </td>
                  {phases.map((phase) => (
                    <td key={phase.name} className="p-2">
                      <div
                        className="rounded-md border border-border px-3 py-2 text-center text-xs"
                        style={{
                          borderLeftColor: dim.color,
                          borderLeftWidth: 3,
                        }}
                      >
                        {perspectiveGrid[dim.name][phase.name]}
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Section 4: The 9 AI Agents */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">The 9 AI Agents</h2>
        <p className="text-muted-foreground">
          Eight specialist agents analyze your business in parallel, each
          bringing a unique expertise. Axiom then challenges their conclusions.
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {agents.map((agent) => (
            <Card key={agent.name}>
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <div
                    className="h-3 w-3 rounded-full"
                    style={{ backgroundColor: agent.color }}
                  />
                  <CardTitle className="text-base">{agent.name}</CardTitle>
                </div>
                <p className="text-xs text-muted-foreground">{agent.role}</p>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {agent.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
        {/* Axiom special card */}
        <Card className="border-[var(--color-agent-axiom)]">
          <CardHeader className="pb-2">
            <div className="flex items-center gap-3">
              <div
                className="h-3 w-3 rounded-full"
                style={{ backgroundColor: axiom.color }}
              />
              <CardTitle className="text-base">{axiom.name}</CardTitle>
              <Badge
                variant="outline"
                className="border-[var(--color-agent-axiom)] text-[var(--color-agent-axiom)]"
              >
                Challenger
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">{axiom.role}</p>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {axiom.description}
            </p>
          </CardContent>
        </Card>
      </section>

      {/* Section 5: The Banking System */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">The Banking System</h2>
        <p className="text-muted-foreground">
          Work progresses through four stages of refinement, from raw analysis
          to published deliverable.
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {bankingStages.map((stage) => (
            <Card key={stage.stage}>
              <CardHeader className="pb-2">
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">
                    {stage.icon}
                  </div>
                  <CardTitle className="text-base">{stage.stage}</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {stage.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Section 6: The Boomerang Process */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">The Boomerang Process</h2>
        <p className="text-muted-foreground">
          The core execution loop that transforms input into validated insights.
        </p>
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col gap-6 md:flex-row md:items-start md:gap-4">
              <div className="flex-1 space-y-2">
                <div className="flex items-center gap-2">
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[var(--color-phase-generate)]/20 text-xs font-bold text-[var(--color-phase-generate)]">
                    1
                  </div>
                  <span className="text-sm font-medium">
                    Parallel Specialist Analysis
                  </span>
                </div>
                <p className="text-sm text-muted-foreground pl-8">
                  All 8 specialist agents analyze the perspective simultaneously,
                  each applying their unique expertise to the input materials.
                </p>
              </div>
              <div className="hidden md:block text-2xl text-muted-foreground">
                &rarr;
              </div>
              <div className="flex-1 space-y-2">
                <div className="flex items-center gap-2">
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[var(--color-agent-axiom)]/20 text-xs font-bold text-[var(--color-agent-axiom)]">
                    2
                  </div>
                  <span className="text-sm font-medium">Axiom Challenge</span>
                </div>
                <p className="text-sm text-muted-foreground pl-8">
                  Axiom reviews all specialist outputs and challenges weak
                  conclusions, unsubstantiated claims, and logical gaps through
                  bounded debate.
                </p>
              </div>
              <div className="hidden md:block text-2xl text-muted-foreground">
                &rarr;
              </div>
              <div className="flex-1 space-y-2">
                <div className="flex items-center gap-2">
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[var(--color-phase-summarize)]/20 text-xs font-bold text-[var(--color-phase-summarize)]">
                    3
                  </div>
                  <span className="text-sm font-medium">Synthesis</span>
                </div>
                <p className="text-sm text-muted-foreground pl-8">
                  Findings are synthesized into a cohesive output incorporating
                  challenges and resolutions, ready for banking and review.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
