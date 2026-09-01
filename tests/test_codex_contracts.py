import json
import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = ROOT / ".codex" / "agents"
SKILL_DIR = ROOT / ".agents" / "skills"

BASELINE_MODELS = {
    "product_planner": ("gpt-5.6-sol", "high"),
    "catalog_architect": ("gpt-5.6-sol", "high"),
    "github_research_curator": ("gpt-5.6-terra", "medium"),
    "catalog_pipeline_builder": ("gpt-5.6-sol", "high"),
    "quality_evaluator": ("gpt-5.6-sol", "high"),
    "evidence_reviewer": ("gpt-5.6-sol", "high"),
    "docs_maintainer": ("gpt-5.6-terra", "medium"),
    "plugin_runtime_builder": ("gpt-5.6-sol", "high"),
    "mcp_backend_builder": ("gpt-5.6-sol", "high"),
}


def load_agent(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def skill_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(?P<body>.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        raise AssertionError(f"missing frontmatter: {path}")
    values = {}
    for line in match.group("body").splitlines():
        if line.startswith((" ", "\t")):
            continue
        key, separator, value = line.partition(":")
        if separator:
            values[key.strip()] = value.strip().strip('\"\'')
    return values


def existing_source_paths(text: str) -> list[Path]:
    """Resolve concrete source paths, excluding conceptual names and globs."""
    paths = re.findall(r"(?<![\w/])(?:[.\w-]+/)*[\w.-]+\.(?:md|json|toml)(?![\w/])", text)
    resolved = [(ROOT / path).resolve() for path in paths]
    for path in resolved:
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise AssertionError(f"missing or out-of-root source: {path}")
    return resolved


class CodexContractTests(unittest.TestCase):
    def test_project_config_uses_gpt56_family_policy(self):
        config = tomllib.loads((ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))
        self.assertEqual(config["model"], "gpt-5.6-sol")
        self.assertEqual(config["model_reasoning_effort"], "high")
        self.assertEqual(config["agents"]["max_concurrent_threads_per_session"], 3)
        self.assertEqual(config["agents"]["default_subagent_model"], "gpt-5.6-terra")
        self.assertEqual(config["agents"]["default_subagent_reasoning_effort"], "medium")

    def test_agents_have_official_fields_baselines_and_resolvable_assignments(self):
        files = sorted(AGENT_DIR.glob("*.toml"))
        self.assertTrue(files)
        names = [load_agent(path)["name"] for path in files]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(set(BASELINE_MODELS) <= set(names))
        discovered_skills = {path.name for path in SKILL_DIR.iterdir() if path.is_dir()}
        supported_fields = {
            "name",
            "description",
            "developer_instructions",
            "model",
            "model_reasoning_effort",
            "sandbox_mode",
        }
        for path in files:
            agent = load_agent(path)
            self.assertEqual(set(agent), supported_fields, f"{path.name}: unsupported runtime field")
            for field in ("name", "description", "developer_instructions"):
                self.assertTrue(agent.get(field), f"{path.name}: missing {field}")
            if agent["name"] in BASELINE_MODELS:
                self.assertEqual((agent["model"], agent["model_reasoning_effort"]), BASELINE_MODELS[agent["name"]])
            self.assertNotIn("skills", agent, f"{path.name}: use repo discovery instead of path-pinned skills.config")
            self.assertNotRegex(path.read_text(encoding="utf-8"), r"[A-Za-z]:[/\\]")
            match = re.search(r"Assigned skills:\s*([^\n.]+)", agent["developer_instructions"])
            self.assertIsNotNone(match, f"{path.name}: missing assigned skills")
            assigned = {value.strip() for value in match.group(1).split(",")}
            self.assertTrue(assigned, f"{path.name}: empty assignment")
            self.assertTrue(assigned <= discovered_skills, f"{path.name}: unknown skill assignment")

    def test_repo_skills_use_official_location_and_metadata(self):
        self.assertFalse((ROOT / ".codex" / "skills").exists())
        skills = sorted(path for path in SKILL_DIR.iterdir() if path.is_dir())
        self.assertTrue(skills)
        for skill in skills:
            frontmatter = skill_frontmatter(skill / "SKILL.md")
            self.assertTrue({"name", "description"} <= set(frontmatter))
            self.assertEqual(frontmatter["name"], skill.name)
            self.assertRegex(frontmatter["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertLessEqual(len(frontmatter["name"]), 64)
            self.assertTrue(frontmatter["description"])
            self.assertLessEqual(len(frontmatter["description"]), 1024)
            metadata = (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
            self.assertIn(f"${skill.name}", metadata)

    def test_skill_activation_spec_covers_all_case_types(self):
        payload = json.loads((ROOT / "evals" / "skills" / "skill-activation-cases.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "spec_present_not_model_run")
        cases = {case["skill"]: case for case in payload["cases"]}
        skills = {path.name for path in SKILL_DIR.iterdir() if path.is_dir()}
        self.assertEqual(set(cases), skills)
        for case in cases.values():
            for case_type in payload["case_types"]:
                self.assertTrue(case.get(case_type))

    def test_agent_routing_spec_covers_every_agent(self):
        payload = json.loads((ROOT / "evals" / "agents" / "agent-routing-cases.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "spec_present_not_model_run")
        agents = {load_agent(path)["name"] for path in AGENT_DIR.glob("*.toml")}
        self.assertEqual({case["expected_agent"] for case in payload["cases"]}, agents)
        ids = [case["case_id"] for case in payload["cases"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_concrete_agent_sources_exist(self):
        for path in AGENT_DIR.glob("*.toml"):
            instructions = load_agent(path)["developer_instructions"]
            source_line = next(line for line in instructions.splitlines() if line.startswith("Sources:"))
            existing_source_paths(source_line)

    def test_source_validator_rejects_broken_and_escaping_paths(self):
        for source in ("PRODUCT_REQUIREMENTS.md", "../outside.md", "docs/missing-contract.md"):
            with self.subTest(source=source), self.assertRaises(AssertionError):
                existing_source_paths(source)

    def test_skill_links_and_current_source_routing(self):
        for path in SKILL_DIR.glob("*/SKILL.md"):
            text = path.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if "://" not in target:
                    resolved = (path.parent / target.split("#")[0]).resolve()
                    self.assertTrue(resolved.is_relative_to(ROOT) and resolved.is_file(), target)
            first_read = next((line for line in text.splitlines() if line.startswith("1. Read ")), "")
            existing_source_paths(re.sub(r"\]\([^)]+\)", "]", first_read))
        taxonomy = (SKILL_DIR / "curate-catalog-taxonomy" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("data/catalog_manifest.json", taxonomy)
        self.assertIn("legacy", taxonomy)

    def test_active_control_plane_has_no_cyrillic_or_corrupt_text(self):
        paths = [ROOT / name for name in ("AGENTS.md", "PLAN.md", "REQUIREMENTS.md", "TEST.md", "EVALS.md")]
        paths += list(AGENT_DIR.glob("*.toml")) + list(SKILL_DIR.glob("*/SKILL.md"))
        paths += list((ROOT / ".codex").glob("*.md"))
        paths += list(SKILL_DIR.glob("*/agents/openai.yaml"))
        paths.append(ROOT / ".codex" / "artifact-templates" / "agent-task-packet.md")
        paths += list((ROOT / "docs" / "plan").glob("*.md"))
        for path in paths:
            self.assertNotRegex(path.read_text(encoding="utf-8"), r"[\u0400-\u04ff\ufffd]", str(path))

    def test_local_and_deferred_case_sets_are_disjoint_and_resolvable(self):
        local = json.loads((ROOT / "evals/agents/team-behavior-cases.json").read_text(encoding="utf-8"))["cases"]
        deferred = json.loads((ROOT / "evals/agents/deferred-extension-cases.json").read_text(encoding="utf-8"))["cases"]
        local_ids = {case["case_id"] for case in local}
        deferred_ids = {case["case_id"] for case in deferred}
        self.assertFalse(local_ids & deferred_ids)
        self.assertEqual(deferred_ids, {"TB-009", "TB-011", "TB-014"})
        self.assertTrue({f"TB-{i:03}" for i in range(15, 23)} <= local_ids)
        self.assertFalse(any(set(case["requirement_ids"]) & {"CP-12", "CP-13", "CP-14"} for case in local))
        agents = {load_agent(path)["name"] for path in AGENT_DIR.glob("*.toml")}
        skills = {path.name for path in SKILL_DIR.iterdir() if path.is_dir()}
        for case in deferred:
            self.assertIn(case["expected_agent"], agents)
            self.assertTrue(set(case["required_skills"]) <= skills)
            self.assertTrue(set(case["requirement_ids"]) & {"CP-12", "CP-13"})

    def test_discovery_metadata_has_bounded_descriptions_and_explicit_prompts(self):
        for path in SKILL_DIR.glob("*/agents/openai.yaml"):
            text = path.read_text(encoding="utf-8")
            description = re.search(r'^\s*short_description:\s*"([^"\n]+)"', text, re.MULTILINE)
            prompt = re.search(r'^\s*default_prompt:\s*"([^"\n]+)"', text, re.MULTILINE)
            self.assertIsNotNone(description, str(path))
            self.assertIsNotNone(prompt, str(path))
            self.assertTrue(25 <= len(description.group(1)) <= 64, str(path))
            self.assertIn(f"${path.parent.parent.name}", prompt.group(1))

    def test_reviewer_remains_read_only(self):
        reviewer = load_agent(AGENT_DIR / "evidence-reviewer.toml")
        self.assertEqual(reviewer["sandbox_mode"], "read-only")

    def test_team_behavior_cases_reference_known_roles_and_skills(self):
        payload = json.loads((ROOT / "evals" / "agents" / "team-behavior-cases.json").read_text(encoding="utf-8"))
        agents = {load_agent(path)["name"] for path in AGENT_DIR.glob("*.toml")}
        skills = {path.name for path in SKILL_DIR.iterdir() if path.is_dir()}
        for case in payload["cases"]:
            self.assertTrue(case["expected_agent"] is None or case["expected_agent"] in agents)
            self.assertTrue(set(case["required_skills"]) <= skills)
        self.assertEqual({case["kind"] for case in payload["cases"]},
                         {"direct", "indirect", "incomplete", "non_trigger", "adversarial", "regression"})


if __name__ == "__main__":
    unittest.main()
