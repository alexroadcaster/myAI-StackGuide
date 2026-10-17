# CP-10 browser acceptance attempt — 2026-10-17

Status: `implemented_local / partially_verified / browser_acceptance_blocked`. CP-10 A-D source is implemented, but the mandatory browser gate has not passed. CP-04 is already owner-accepted; this report does not reopen it or start CP-11. [Machine-readable receipt](cp10-browser-acceptance-2026-10-17.json) binds this attempt and the inspected bytes.

## Observed blocker

The current Codex in-app browser rejected direct `file:` navigation to the existing CP-10 synthetic session artifact. Its URL policy reported only HTTP/HTTPS as supported and explicitly forbade achieving the same outcome through alternate browser surfaces, a proxy/server, indirect execution or raw CDP. No rendered page loaded and zero browser acceptance checks or screenshots were obtained. No alternate navigation, local server or permission change followed the denial. Selecting/inventorying available browsers before the attempt did not provide rendered evidence.

An authorized browser QA request does not override the tool's URL policy. Static checks cannot close this mandatory rendered gate. This is a fresh2026-10-17 refusal, not an assumption from the earlier refusal.

## Reviewable artifact and current source check

Open the [synthetic eight-view preview](../../.codex-tmp/cp10-d-preview/docs/myai-stackguide/status.html) manually in a browser for independent owner review. It contains demonstration data, not an inspected user project or a current catalog recommendation.

The existing CP-07 adapter validated the saved fixture and one ledger-selected immutable historical run, then recomputed the expected HTML in memory. Current renderer output exactly matches the retained123,344-byte preview at saved revision3. SHA256: `e92152682fd31afdac23b349196bd8b286fd15ef8b291fc9572e3185ed17e4b9`. State, immutable run files and HTML were read only. No renderer/state change or runtime test rerun was required. This establishes source-to-preview parity only; historical16/16 artifact checks remain historical.

## Manual browser acceptance checklist

Record PASS/FAIL with browser/version, dimensions and an observation or screenshot for each group. A missing check remains pending; do not turn this checklist into a blanket acceptance statement. Do not install dependencies, execute copied commands, submit forms, change domain state or use production/private data.

| ID | Required observation | Current rendered result |
| --- | --- | --- |
| UI-01 | Open Goal, Questions, Scan, Context, Options, Compare, Integration and History in RU, then EN; all16 view/language combinations are readable with truthful unknowns. | Not executed |
| UI-02 | At1280,1440 and1920 CSS-pixel desktop widths, navigation and long prose remain readable; narrow desktop comparison retains accessible controls. Mobile is excluded. | Not executed |
| UI-03 | Navigate using Tab/Shift+Tab and Enter; skip link reaches main, focus is visible and never left in a hidden section. Back/Forward and an invalid fragment return to a usable view. | Not executed |
| UI-04 | At200% zoom, content, language switch, disclosure and comparison remain operable without overlap or lost controls; reset zoom afterward. | Not executed |
| UI-05 | Print preview retains the content, references, caveats and proposed-versus-executed distinction; navigation chrome does not hide necessary content. Cancel without printing if no output is needed. | Not executed |
| UI-06 | With JavaScript unavailable in the isolated test tab, saved-language markup and all sections remain readable; no unusable active controls are falsely offered. | Not executed |
| UI-07 | Copy an actual handoff; when clipboard is unavailable/denied, the text can be selected manually and visible feedback explains fallback. Do not execute the copied text. | Not executed |
| UI-08 | Locale switch preserves IDs, URLs, selected candidates, evidence, constraints and action authority. Missing translations remain labeled with original text rather than invented translation. | Not executed |
| UI-09 | Check saved-start/partial/no-memo and immutable-history/recovery fixtures as applicable; unavailable history is explicit and an old HTML snapshot never claims a failed later publication succeeded. | Not executed |
| UI-10 | In offline mode no unexpected requests or external assets are needed. Browser-only view/locale/disclosure changes leave state.json and immutable runs unchanged. | Not executed |

The prepared full-state fixture supports most groups, but does not alone cover every empty/error/fallback fixture. Those states must be rendered and checked when browser access is permitted; source assertions are not their visual evidence. The accepted [workspace design](../plan/plugin-v1-session-workspace-design.md) and [contract](../../specs/artifact/session-workspace-contract.md) remain normative.

## Smallest next action

Either restore a policy-permitted browser-tool path for the local artifact, or have the owner independently perform the manual review and provide actual results for the checklist. Opening a page or accepting a screenshot alone does not complete all groups. The agent cannot bypass this URL denial by serving the blocked artifact through HTTP or switching browser surfaces.

CP-10 remains partially verified; CP-11's CP-10 browser prerequisite stays open. CP-11 lifecycle, CP-15 wider product usefulness/privacy and CP-16 release acceptance remain separate. No installation, external publication, Git history, scanner execution or credentials were used.
