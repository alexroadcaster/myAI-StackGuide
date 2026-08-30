# myAI-StackGuide Context Scanner

## One-Sentence Idea

The myAI-StackGuide Context Scanner lets users load myAI-StackGuide into their own product, repository, or workspace so it can understand the product context before recommending open-source repositories from the curated catalog.

The scanner is read-only. It gathers context, summarizes the product, identifies gaps, and improves repository recommendations. It does not modify code, install packages, create pull requests, or implement features.

## Product Thesis

Many users cannot accurately describe the technical shape of their product. Founders, operators, product managers, and non-technical owners often know the goal and pain points, but not the stack, architecture, dependencies, integration surface, or hidden constraints.

If the guide only asks the user what they need, it may recommend generic repositories. If it can also inspect the project safely, it can produce context-aware recommendations:

- What kind of product is this?
- What stack is already in use?
- What capabilities already exist?
- Which gaps are visible?
- Which repository categories are actually relevant?
- Which repositories should be studied, adopted, compared, or avoided?

The stronger metaphor is:

> The guide does not only wait inside the library. It can visit the user's workshop, inspect what is already built, ask clarifying questions, and then recommend the right books.

## Product Positioning

This feature turns myAI-StackGuide into a context-aware open-source adoption advisor.

It helps users answer:

- What open-source projects are relevant to my actual product?
- What repositories should I inspect first given my current stack?
- What category path matches the product I already have?
- Which famous repositories are distractions for my stage?
- What gaps in my product suggest a need for document parsing, RAG, evals, support tooling, automation, analytics, security, or operations software?
- What should my team compare before adopting anything?

It is not a coding assistant, migration tool, dependency updater, security scanner, or procurement authority.

## User Types

### Non-Technical Founder

Knows the business goal, market, and customer pain, but cannot explain the codebase or architecture.

Needs:

- A plain-language product context brief.
- A shortlist of repositories to discuss with a technical partner.
- A warning about what is too early, too complex, or mismatched.

### Product Manager

Understands workflows and user needs, but may not know whether the product needs a library, platform, internal tool, or reference implementation.

Needs:

- Category path.
- Compare view.
- Build-versus-buy framing.
- Decision memo for team review.

### Engineer Or Technical Lead

Understands the stack, but wants a faster open-source landscape review grounded in the existing project.

Needs:

- Repository shortlist by role.
- Technical caveats.
- Reading path.
- Freshness and verification signals.

### Internal Operator

Works in support, sales, analytics, finance, or operations and wants to improve workflows without knowing the implementation details.

Needs:

- Business workflow interpretation.
- Adjacent categories.
- Self-hosted and automation options.
- Risk framing.

## Core Workflow

1. **Load**
   The user connects the guide to a repository, uploaded archive, local workspace summary, or embedded product context provider.

2. **Permission Review**
   The product shows what will be scanned, what will be ignored, what leaves the user's environment, and what is stored.

3. **Read-Only Scan**
   The scanner inspects allowed files and metadata without modifying the project.

4. **Context Extraction**
   The scanner extracts product type, stack, architecture signals, domain entities, integrations, maturity, and visible gaps.

5. **User Interview**
   The guide asks a small number of plain-language questions to understand goals, constraints, and stage.

6. **Project Context Brief**
   The guide produces a concise description of the product and detected constraints.

7. **Repository Matching**
   The guide maps the context to task archetypes, category paths, stack recipes, and repository cards.

8. **Recommendation Memo**
   The guide returns a shortlist, avoid/defer list, compare view, reading path, caveats, and next decision.

## Deployment Modes

### Hosted Web App

Best for founders, product managers, and non-technical users.

Possible inputs:

- GitHub read-only connection.
- Uploaded repository archive.
- Uploaded documentation pack.
- Product questionnaire.
- Existing decision board.

Benefits:

- Lowest onboarding friction.
- Good for advisory workflows.
- Centralized decision memo and saved boards.

Risks:

- Requires strong privacy messaging.
- Requires careful data retention controls.
- May not be acceptable for sensitive private codebases.

### Local CLI Scanner

Best for technical users and teams with stricter privacy requirements.

The CLI runs locally, creates a sanitized project summary, and sends only the summary to the hosted recommendation service or saves it for local use.

Benefits:

- Keeps raw code local.
- Easier to exclude sensitive files.
- Better for enterprise or private repositories.

Risks:

- Higher setup friction.
- Requires versioned scanner behavior.
- Needs robust redaction and allowlist rules.

### Embeddable SDK Or Widget

Best for products that want the guide inside their own user experience.

Possible placements:

- Product admin panel.
- Developer portal.
- Internal platform.
- AI assistant sidebar.
- Marketplace or integration hub.

Benefits:

- The guide can use product-native context.
- Good for recurring recommendations.
- Can support decision boards and watchlists.

Risks:

- Requires clear API contracts.
- Needs tenant isolation.
- Requires strict permission scopes.

### MCP-Based Context Provider

Best for advanced users and agentic workspaces.

A read-only MCP server can expose approved project context resources to the guide.

Potential resources:

- `project://summary`
- `project://stack`
- `project://dependencies`
- `project://routes`
- `project://schemas`
- `project://docs`
- `project://integrations`

Benefits:

- Works well with agentic tools.
- Keeps context access explicit.
- Separates scanner implementation from recommendation logic.

Risks:

- MCP is an interface layer, not the product brain.
- Requires careful resource design and least-privilege defaults.

## Permission And Privacy Model

The scanner should operate on least privilege.

Default stance:

- Read-only access.
- No code modification.
- No package installation.
- No command execution unless explicitly enabled for local scanner metadata collection.
- No secret collection.
- No customer data collection.
- No private data retention by default.
- Explicit user consent before external transmission.

The product should show:

- What sources will be read.
- What sources will be ignored.
- Whether raw files leave the environment.
- Whether summaries are stored.
- How long summaries are retained.
- Which users or team members can view the decision board.

## Scan Sources

The scanner should use an allowlist-first approach.

High-value sources:

| Source | Extracted signals |
|---|---|
| `README`, docs, guides | Product purpose, setup, users, positioning, workflows |
| `package.json`, `pnpm-lock.yaml`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml` | Languages, frameworks, runtime, dependencies |
| App routes and page structure | Product surface, user flows, dashboards, portals, API shape |
| API handlers and OpenAPI specs | Integration surface, external systems, backend maturity |
| Database schemas and migrations | Domain entities, product model, operational complexity |
| Docker and deployment config | Deployment model, infrastructure assumptions |
| Test and eval files | Maturity, reliability posture, AI evaluation readiness |
| Changelog and release notes | Product direction and recent activity |
| Issue templates and roadmap docs | Known problems, planned work, team priorities |
| Existing agent or prompt files | AI workflow patterns, constraints, guardrails |

Optional sources with stricter controls:

- Screenshots or design exports.
- Product analytics schema.
- Support docs.
- Public website copy.
- User-provided business brief.

## Excluded Sources

The scanner should ignore sensitive or high-risk files by default.

Always excluded unless explicitly overridden in a local-only mode:

- `.env`
- `.env.*`
- private keys
- API tokens
- credentials
- database dumps
- customer exports
- billing exports
- production logs
- raw user messages
- private analytics events
- local cache directories
- generated dependency folders such as `node_modules`
- build outputs such as `dist`, `build`, `.next`, `target`

The scanner should prefer structured summaries over raw file retention.

## Project Context Brief

The Project Context Brief is the bridge between project scanning and repository recommendation.

Recommended schema:

```yaml
project_context_brief:
  product_name: string
  product_type: string
  target_users:
    - string
  project_stage: research | prototype | pilot | production_candidate | production | unknown
  detected_stack:
    languages:
      - string
    frameworks:
      - string
    databases:
      - string
    infrastructure:
      - string
    ai_services:
      - string
  product_surface:
    - dashboard
    - api
    - mobile_app
    - browser_extension
    - cli
    - workflow_tool
    - ai_assistant
  domain_entities:
    - string
  detected_integrations:
    - string
  detected_capabilities:
    - string
  possible_gaps:
    - string
  relevant_task_archetypes:
    - string
  relevant_category_paths:
    - string
  recommendation_mode: learn | compare | prototype | adopt | defer
  confidence:
    product_understanding: low | medium | high
    technical_stack: low | medium | high
    recommendation_readiness: low | medium | high
  caveats:
    - string
```

The brief should be understandable by a non-technical user and precise enough for a technical reviewer.

## Context Extraction Heuristics

The scanner should infer signals conservatively.

Examples:

- A Next.js app with dashboard routes, Stripe dependency, and organization tables likely indicates a SaaS product.
- A project with document parsers, vector database dependencies, and prompt files likely belongs near RAG, retrieval, memory, and eval categories.
- A repository with many workflow connectors and queue libraries may need automation and durable workflow recommendations.
- A support portal with tickets, conversations, and knowledge base entities should map to customer support, documents, RAG, and analytics categories.
- A project with weak tests or no eval artifacts should receive caution before adopting complex AI orchestration repositories.

The guide should mark inferred claims as inferred. It should not present guesses as facts.

## Recommendation Output

The final recommendation should include:

1. **Product understanding**
   A short explanation of what the guide believes the product is.

2. **Detected constraints**
   Stack, stage, domain, deployment, data sensitivity, and team constraints.

3. **Relevant category path**
   The shelves that match the actual product context.

4. **Shortlist**
   Five to twelve repositories grouped by role.

5. **Why these**
   Fit explanation grounded in the project context brief.

6. **Avoid or defer**
   Repositories, categories, or architecture paths that are not appropriate yet.

7. **Compare view**
   What the user should compare before making a decision.

8. **Reading path**
   What to inspect first in the recommended repositories.

9. **Caveats**
   Freshness, license, maturity, security, and missing-context warnings.

10. **Next decision**
   A human decision, not an implementation instruction.

## Example Output Shape

```text
Product understanding:
This appears to be a B2B SaaS support dashboard with knowledge-base search and customer conversation workflows.

Detected constraints:
Next.js application, PostgreSQL schema, Stripe billing, support-ticket entities, and early AI integration signs. No visible eval layer was detected.

Relevant category path:
Customer Support & Success -> Documents, OCR & Parsing -> RAG, Retrieval & Search -> Evals, Observability & Prompt Ops -> Automation, Workflows & No-code.

Primary candidates:
1. documenso/documenso - inspect if signed document workflows matter.
2. infiniflow/ragflow - inspect as a heavier RAG product reference.
3. langfuse/langfuse - inspect for AI observability and eval workflow.

Supporting tools:
4. n8n-io/n8n - compare only if workflow automation is a core requirement.
5. microsoft/markitdown - inspect as a document ingestion utility.

Avoid for now:
- Full autonomous agent frameworks if the current bottleneck is support knowledge quality.
- Heavy workflow orchestration if ticket routing is still manual and undefined.

Next decision:
Do you need to improve document answer quality first, or support workflow routing first?
```

## Product Architecture

### Layer 1: Context Access

Inputs:

- GitHub read-only app.
- Uploaded archive.
- Local CLI summary.
- Embedded SDK context.
- Read-only MCP resources.

Output:

- Allowed file inventory.
- Sanitized project facts.
- Scan metadata.

### Layer 2: Context Normalization

Inputs:

- File inventory.
- Structured metadata.
- User interview answers.

Output:

- Project Context Brief.
- Confidence scores.
- Missing-context questions.

### Layer 3: Repository Matching

Inputs:

- Project Context Brief.
- Repository cards.
- Task archetypes.
- Stack recipes.
- Compare views.
- Policy profiles.

Output:

- Candidate repository set.
- Role assignments.
- Avoid/defer candidates.

### Layer 4: Advisory Response

Inputs:

- Candidate set.
- Context brief.
- Freshness and trust signals.

Output:

- Recommendation memo.
- Compare view.
- Reading path.
- Caveats.
- Next decision.

## Safety Boundaries

The embedded guide must keep the same advisory-only rule as myAI-StackGuide.

It can:

- Scan allowed project context.
- Summarize product and technical signals.
- Ask clarifying questions.
- Recommend repositories.
- Build comparison frames.
- Export decision memos.
- Warn about stale, mismatched, or risky options.

It cannot:

- Edit project files.
- Install dependencies.
- Run migrations.
- Create pull requests.
- Write implementation code.
- Execute arbitrary commands in hosted mode.
- Claim security, legal, or procurement approval.
- Send private data to third parties without explicit user consent.

Project scan is context acquisition, not implementation.

## Data Retention

Default retention should be conservative.

Recommended modes:

- **Ephemeral**: scan summary is used for one session and deleted.
- **Saved decision board**: user explicitly saves context brief, recommendations, and notes.
- **Team workspace**: organization controls retention policy and member access.
- **Local-only**: scanner writes a local summary and does not upload raw code.

Stored artifacts should avoid raw source code unless the user explicitly chooses a mode that needs it.

## Trust And Confidence

Every recommendation should expose confidence.

Recommended confidence dimensions:

- Project understanding.
- Stack detection.
- Domain interpretation.
- Repository metadata freshness.
- Recommendation fit.
- Missing context risk.

If confidence is low, the guide should ask a focused question or present a tentative recommendation with caveats.

## Evaluation Scenarios

The feature needs evals that cover both technical and non-technical users.

Example eval scenarios:

- Non-technical founder connects a SaaS repository and asks what open-source tools could improve support.
- Product manager uploads docs for an internal workflow product and asks what categories matter.
- Engineer scans a RAG prototype and asks what to compare before production pilot.
- Operator connects a CRM-like internal tool and asks for automation recommendations.
- User provides very little explanation, but the repository clearly shows a document-heavy AI product.
- Repository contains sensitive-looking file names that must be excluded from scan output.

Eval criteria:

- Did the scanner avoid excluded files?
- Did it produce a useful project context brief?
- Did it separate facts from inferences?
- Did it ask only necessary clarifying questions?
- Did it choose relevant category paths?
- Did it avoid generic popular recommendations?
- Did it produce useful avoid/defer guidance?
- Did it preserve the no-code advisory boundary?

## V1 Scope

The first useful implementation should be narrow and trust-preserving.

Recommended V1:

- Hosted GitHub read-only repository connection.
- Uploaded archive support for users without GitHub connection.
- Allowlist-based scanner.
- Basic redaction and exclusion rules.
- Project Context Brief generation.
- One short user interview flow.
- Context-aware repository shortlist.
- Avoid/defer recommendations.
- Compare view.
- Decision memo export.
- Saved decision board.
- Manual curator review for scanner failures and poor recommendations.

Out of scope for V1:

- Code modifications.
- Dependency installation.
- Pull request creation.
- Automated migrations.
- Full security scanning.
- Legal or license approval.
- Production procurement decisions.
- Broad autonomous agent orchestration.

## Open Product Risks

### Privacy Trust

Users may hesitate to connect private repositories. The product must make scan scope, exclusions, and retention obvious.

### False Understanding

The scanner can infer the wrong product type from partial files. The brief must show confidence and allow user correction.

### Over-Recommendation

The guide may recommend advanced repositories when the product only needs a simple workflow improvement. Avoid/defer guidance is required.

### Non-Technical Misinterpretation

Non-technical users may treat recommendations as implementation instructions. The output must make the next decision clear and avoid coding steps.

### Sensitive Data Leakage

Allowlist scanning, redaction, local-only mode, and explicit retention controls are necessary before private repository usage.

## Durable Product Principle

The embedded scanner should make recommendations more grounded without turning the guide into an implementation agent.

The product wins when a non-technical user can say:

> I did not know what was inside my product technically. The guide inspected it safely, explained it clearly, and gave me a repository shortlist that my team could evaluate.
