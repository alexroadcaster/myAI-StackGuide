"""Product decision guidance shared by Markdown and HTML catalog builders."""

from __future__ import annotations


WHEN_TO_USE = [
    {
        "situation": "You need a shortlist before choosing an AI or automation stack.",
        "start": "Search by workflow, then inspect the matching category and top repositories.",
        "outcome": "A focused list of projects to read, prototype, or compare.",
    },
    {
        "situation": "You are deciding what to self-host, buy, fork, or ignore.",
        "start": "Use the business/product categories alongside engineering platform categories.",
        "outcome": "A decision map for build-versus-buy and adoption planning.",
    },
    {
        "situation": "You are designing an agentic workflow and need adjacent components.",
        "start": "Move across runtime, tools, memory, retrieval, evals, execution, and UI categories.",
        "outcome": "A stack-shaped view instead of isolated repository bookmarks.",
    },
    {
        "situation": "You are auditing a personal fork library or research queue.",
        "start": "Use source groups, scores, categories, and stale metadata caveats.",
        "outcome": "A cleaner queue of active candidates, references, and archive/delete items.",
    },
]


WHEN_TO_AVOID = [
    {
        "need": "Security, compliance, legal, or procurement approval.",
        "reason": "The catalog is not a security audit, license opinion, vendor review, or production-readiness certification.",
        "better": "Run dedicated code, security, license, and vendor due diligence.",
    },
    {
        "need": "Realtime repository rankings.",
        "reason": "Stars, forks, update timestamps, and licenses are snapshot metadata and drift quickly.",
        "better": "Refresh from the GitHub API before presenting current claims.",
    },
    {
        "need": "An exhaustive market map.",
        "reason": "The catalog is curated for practical decision support, not complete market coverage.",
        "better": "Run a scoped research refresh with explicit search queries and inclusion rules.",
    },
    {
        "need": "A direct product recommendation for a high-stakes adoption.",
        "reason": "Scores are triage signals and are not comparable to hands-on evaluation in your environment.",
        "better": "Prototype the top candidates against your workload, data, permissions, and failure modes.",
    },
]


STACK_RECIPES = [
    {
        "name": "Coding Agent Delivery Loop",
        "use_when": "You want agents to plan, edit, run tools, evaluate changes, and ship safely.",
        "path": [
            "Codex, Claude & Skill Workflows",
            "Agent Runtime & Orchestration",
            "MCP & Tool Integrations",
            "Sandboxed Code Execution",
            "Evals, Observability & Prompt Ops",
            "Security, Safety & Supply Chain",
        ],
        "question": "Which parts of the loop must be reliable before autonomy increases?",
    },
    {
        "name": "RAG Knowledge Product",
        "use_when": "You need a product that reads documents, retrieves context, remembers decisions, and cites sources.",
        "path": [
            "Documents, OCR & Parsing",
            "RAG, Retrieval & Search",
            "Vector DBs & Embedding Infrastructure",
            "Memory & Context Systems",
            "Knowledge Graphs",
            "Evals, Observability & Prompt Ops",
        ],
        "question": "Is the bottleneck ingestion quality, retrieval quality, memory, or evaluation?",
    },
    {
        "name": "Business Ops Automation Stack",
        "use_when": "You want to connect internal workflows across leads, support, reporting, and back office.",
        "path": [
            "Automation, Workflows & No-code",
            "Sales, CRM & Lead Generation",
            "Customer Support & Success",
            "Analytics, BI & Reporting",
            "Accounting, Finance & ERP",
            "Legal, Contracts & Compliance",
        ],
        "question": "Which system owns customer, revenue, and compliance state?",
    },
    {
        "name": "Founder Lean Operating System",
        "use_when": "You need a lightweight startup stack before buying multiple SaaS products.",
        "path": [
            "Market Research & Competitive Intelligence",
            "Marketing, Growth & SEO",
            "Sales, CRM & Lead Generation",
            "Product Management, Roadmaps & Feedback",
            "Analytics, BI & Reporting",
            "Automation, Workflows & No-code",
        ],
        "question": "What should be self-hosted, bought, or deferred for the next 90 days?",
    },
    {
        "name": "Design-To-Prototype Loop",
        "use_when": "You want to move from product idea to interface, demo, or user-testable prototype.",
        "path": [
            "Design, Brand & UI/UX",
            "Frontend, UI, Desktop & Browser Automation",
            "Codex, Claude & Skill Workflows",
            "Multimodal & Vision Agents",
            "Developer Tools & CLI",
        ],
        "question": "Which artifact is the next decision point: design system, prototype, demo, or production UI?",
    },
]


COMPARE_VIEWS = [
    {
        "name": "Agent runtimes vs workflow engines",
        "decides": "Whether you need autonomous agent behavior, deterministic orchestration, or both.",
        "categories": ["Agent Runtime & Orchestration", "Workflow State Machines & Durable Agents"],
    },
    {
        "name": "RAG vs memory vs knowledge graphs",
        "decides": "Whether the problem is retrieval, long-lived context, entity relationships, or source-grounded answers.",
        "categories": ["RAG, Retrieval & Search", "Memory & Context Systems", "Knowledge Graphs"],
    },
    {
        "name": "MCP integrations vs no-code automation",
        "decides": "Whether agents need programmable tool access or business teams need workflow automation.",
        "categories": ["MCP & Tool Integrations", "Automation, Workflows & No-code"],
    },
    {
        "name": "Evals/observability vs security/safety",
        "decides": "Whether the immediate risk is quality drift, prompt behavior, unsafe execution, or supply-chain exposure.",
        "categories": ["Evals, Observability & Prompt Ops", "Security, Safety & Supply Chain"],
    },
    {
        "name": "Self-hosted suite vs focused tool",
        "decides": "Whether to adopt a broad operating platform or combine narrow tools around one workflow.",
        "categories": ["Operations, Project Management & Internal Tools", "Analytics, BI & Reporting", "Customer Support & Success"],
    },
]


def _pipe_list(values: list[str]) -> str:
    return " -> ".join(values)


def markdown_section(level: int = 2) -> str:
    heading = "#" * level
    child = "#" * (level + 1)
    lines = [
        f"{heading} Product Decision Layer",
        "",
        "Use this catalog as a decision aid: start from the work you need to do, narrow to the right category path, then inspect repositories with their caveats in mind.",
        "",
        f"{child} When To Use",
        "",
        "| Situation | Start With | Decision Output |",
        "|---|---|---|",
    ]
    for item in WHEN_TO_USE:
        lines.append(f"| {item['situation']} | {item['start']} | {item['outcome']} |")

    lines.extend(
        [
            "",
            f"{child} When To Avoid",
            "",
            "| Need | Why This Catalog Is Not Enough | Better Next Step |",
            "|---|---|---|",
        ]
    )
    for item in WHEN_TO_AVOID:
        lines.append(f"| {item['need']} | {item['reason']} | {item['better']} |")

    lines.extend(
        [
            "",
            f"{child} Stack Recipes",
            "",
            "| Recipe | Use When | Category Path | Decision Question |",
            "|---|---|---|---|",
        ]
    )
    for recipe in STACK_RECIPES:
        lines.append(
            f"| {recipe['name']} | {recipe['use_when']} | {_pipe_list(recipe['path'])} | {recipe['question']} |"
        )

    lines.extend(
        [
            "",
            f"{child} Compare Views",
            "",
            "| Compare | Use This View To Decide | Categories |",
            "|---|---|---|",
        ]
    )
    for view in COMPARE_VIEWS:
        lines.append(f"| {view['name']} | {view['decides']} | {_pipe_list(view['categories'])} |")

    lines.append("")
    return "\n".join(lines)


def payload() -> dict:
    return {
        "whenToUse": WHEN_TO_USE,
        "whenToAvoid": WHEN_TO_AVOID,
        "stackRecipes": STACK_RECIPES,
        "compareViews": COMPARE_VIEWS,
    }
