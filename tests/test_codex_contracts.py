import json
import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = ROOT / ".codex" / "agents"
SKILL_DIR = ROOT / ".agents" / "skills"

EXPECTED_MODELS = {
    "product_planner": ("gpt-5.6-sol", "high"),
    "catalog_architect": ("gpt-5.6-sol", "high"),
    "github_research_curator": ("gpt-5.6-terra", "medium"),
    "catalog_pipeline_builder": ("gpt-5.6-sol", "high"),
    "quality_evaluator": ("gpt-5.6-sol", "high"),
    "evidence_reviewer": ("gpt-5.6-sol", "high"),
    "docs_maintainer": ("gpt-5.6-terra", "medium"),
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
        key, separator, value = line.partition(":")
        if separator:
            values[key.strip()] = value.strip()
    return values


class CodexContractTests(unittest.TestCase):
    def test_project_config_uses_gpt56_family_policy(self):
        config = tomllib.loads((ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))
        self.assertEqual(config["model"], "gpt-5.6-sol")
        self.assertEqual(config["model_reasoning_effort"], "high")
        self.assertEqual(config["agents"]["max_concurrent_threads_per_session"], 3)
        self.assertEqual(config["agents"]["default_subagent_model"], "gpt-5.6-terra")
        self.assertEqual(config["agents"]["default_subagent_reasoning_effort"], "medium")

    def test_agents_have_official_fields_models_and_three_assignments(self):
        files = sorted(AGENT_DIR.glob("*.toml"))
        self.assertEqual(len(files), len(EXPECTED_MODELS))
        discovered_skills = {path.name for path in SKILL_DIR.iterdir() if path.is_dir()}
        for path in files:
            agent = load_agent(path)
            for field in ("name", "description", "developer_instructions"):
                self.assertTrue(agent.get(field), f"{path.name}: missing {field}")
            self.assertIn(agent["name"], EXPECTED_MODELS)
            self.assertEqual((agent["model"], agent["model_reasoning_effort"]), EXPECTED_MODELS[agent["name"]])
            self.assertNotIn("skills", agent, f"{path.name}: use repo discovery instead of path-pinned skills.config")
            self.assertNotRegex(path.read_text(encoding="utf-8"), r"[A-Za-z]:[/\\]")
            match = re.search(r"Assigned skills:\s*([^\n.]+)", agent["developer_instructions"])
            self.assertIsNotNone(match, f"{path.name}: missing assigned skills")
            assigned = {value.strip() for value in match.group(1).split(",")}
            self.assertEqual(len(assigned), 3, f"{path.name}: expected three assigned skills")
            self.assertTrue(assigned <= discovered_skills, f"{path.name}: unknown skill assignment")

    def test_repo_skills_use_official_location_and_metadata(self):
        self.assertFalse((ROOT / ".codex" / "skills").exists())
        skills = sorted(path for path in SKILL_DIR.iterdir() if path.is_dir())
        self.assertEqual(len(skills), 11)
        for skill in skills:
            frontmatter = skill_frontmatter(skill / "SKILL.md")
            self.assertEqual(set(frontmatter), {"name", "description"})
            self.assertEqual(frontmatter["name"], skill.name)
            self.assertIn("Use ", frontmatter["description"])
            self.assertIn("do not use", frontmatter["description"].lower())
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
        self.assertEqual({case["expected_agent"] for case in payload["cases"]}, set(EXPECTED_MODELS))


if __name__ == "__main__":
    unittest.main()
