# CP-10 browser policy diagnosis and minimal origin proposal — 2026-10-17

Status: `proposal_prepared_not_applied`. [Sanitized inspection receipt](cp10-browser-policy-2026-10-17.json) and [inactive TOML fragment](cp10-loopback-8765.proposed.toml). This task inspects settings and prepares an exception; no live policy is changed, no server starts and no browser rejection is bypassed.

## Concrete finding

The confirmed failure is Browser Use's URL-protocol gate: it rejects `file:` and reports only HTTP/HTTPS as allowed protocols. Both direct file navigation and observation of the user's already-open local tab were rejected. Chrome's enabled file-URL permission is separate. This establishes the failing check, but does not identify an editable local file or the internal implementation owner of that gate.

There is no observed refusal for `http://127.0.0.1:8765`: it was not contacted. Do not label the port blocked or allowed without actual authorized evidence. A user-origin allow rule does not prove that the existing explicit no-workaround restriction has been lifted.

## Inspected configuration layers

| Layer | Observed result |
| --- | --- |
| Project `.codex/config.toml` | Present; no `browser_use`, browser/network feature overrides or permission profiles. |
| `%USERPROFILE%/.codex/config.toml` | Present; no `browser_use` rules or browser-related feature overrides. Values include workspace-write, on-request, reviewer=user and default_permissions=:workspace. These are file values, not proof of the running browser tool's effective approvals. |
| Ancestor project config candidates | No additional files found at the inspected parent locations. |
| `%ProgramData%/OpenAI/Codex/requirements.toml` | Absent at the documented Windows system-policy path. |
| System config/legacy managed candidates | No files at the inspected documented-system/default and legacy candidate locations. |
| Desktop persisted app state | No effective browser-origin policy table exposed in the inspected top-level browser key names. No unrelated account/browser/task values are retained. |
| Cloud/managed effective policy | Not verified. Absence of local files does not establish absence of cloud or session controls. |

The installed npm CLI reports0.163.0. Its read-only existing app-server proxy did not return configuration: the local control socket was unreachable (OS error10050). No daemon was started, restarted or installed. A child PowerShell wrapper initially failed execution policy; one retry used the existing native CMD shim without changing execution policy. CLI arg0 ACL warnings were recorded once and not repaired. A separate new CLI server would not by itself prove this desktop browser session's policy, so none was launched.

## Minimum proposed exception

```toml
[browser_use.origins."http://127.0.0.1:8765"]
access = "allow"
uploads = "deny"
downloads = "deny"
full_cdp_access = "deny"
persistent_approval = false
access_approval_lifetime = "turn"
```

The exact origin includes scheme, IP and port; it grants neither localhost aliases, other ports, HTTPS nor file URLs. Other sites and defaults remain unchanged. The one-turn approval lifetime avoids persistent approval. Existing automatic review remains enabled/unchanged. No global network, Full Access, shell approval, history, CDP or extension-permission change is proposed.

This is a merge fragment for a supported user `config.toml` browser policy layer, not a replacement file and not a newly enforced system `requirements.toml`. On a managed client, higher-priority requirements and matching denies still win. `access=allow` only lets the normal approval/policy checks continue; it does not create an approval. Syntax has been checked using Python tomllib; loaded support in this desktop version is not yet verified. The user config hash is recorded before any proposed application.

Origin rules cannot restrict URL paths or HTTP methods. If the workflow is subsequently authorized, its temporary server must enforce a fixed synthetic-fixture allowlist, GET/HEAD only, no directory listing, no state/run JSON, no repository/private files, no write route, no redirects/symlink escape, no external resources and loopback-only binding. Serving the repository root is outside this proposal. The listener must stop after the check. No such listener was started here.

The base exception intentionally keeps full CDP denied. It enables consideration of normal page observation/interaction only. Print, JavaScript-disabled and offline checks require confirming the available approved test capabilities; no claim that this one rule alone completes every CP-10 check is made.

## Activation and remaining boundary

1. Review and explicitly authorize the separate synthetic HTTP-preview workflow and exact origin policy. The present request authorized preparation only.
2. Have the applicable policy authority apply the narrow exception; do not overwrite unrelated user configuration or attempt to relax a managed deny through a lower layer.
3. Obtain effective-policy/normal tool approval evidence for that origin and workflow. A config-file edit or new chat alone is not proof that the earlier no-workaround instruction is superseded.
4. Only after that boundary is resolved, run the approved preview and browser matrix, retaining source hashes, screenshots, interactions and residual gaps. Manual user UI testing is not intrinsic to this proposed workflow.
5. Roll back by removing only the introduced origin table or restoring any pre-existing exact-origin values from a backup, preserving subsequent edits. If permission was granted in the app UI, revoke that specific exception there. Stop the test listener.

CP-10 remains partially verified. CP-04's accepted record and all CP-11/15/16 gates are unchanged.

## Sources

- [Configuration precedence](https://learn.chatgpt.com/docs/config-file/config-basic#configuration-precedence).
- [Managed requirements and browser controls](https://learn.chatgpt.com/docs/enterprise/managed-configuration#control-browser-and-computer-use).
- [Browser-origin field reference](https://learn.chatgpt.com/docs/config-file/config-reference).
- [Read effective admin requirements](https://learn.chatgpt.com/docs/app-server#read-admin-requirements-configrequirementsread).
- [Supported browser preview workflow](https://learn.chatgpt.com/docs/browser#preview-a-page).
