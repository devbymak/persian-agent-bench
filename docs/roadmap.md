# Roadmap

Version 0.1 tests one kind of agent: an assistant that reads a person's mail, chats, files and calendar. The design already fits other agents: cases name abstract tools, runners skip cases whose tools they lack, and checks read a neutral trace. What is narrow is the scenarios. The plan widens them inside this one dataset rather than in separate sets.

## One dataset, several agent profiles

Every case gets a `profile` field so a runner can pick the cases that fit its agent. `tools_required` keeps working as before.

| Profile | Agent | Release |
|---|---|---|
| `assistant` | Reads mail, chats, files and calendar for a person (all 0.1 cases) | 0.1 |
| `coding` | Works in a code repository: reads code, issues and CI, edits files, runs commands | 0.2 |
| `browsing` | Searches and reads the web for the user | 0.2 |
| `tool_output` | Calls outside tools (MCP servers, APIs) and reads their descriptions and results | 0.2 |
| `support` | Answers customers from tickets and account records | 0.3 |
| `rag` | Answers from retrieved documents, with no tools | 0.3 |
| `multi_agent` | Receives work from another agent | 0.3 |

## 0.2 scope

About 8 attack families per new profile, each with a plain and a disguised case, plus 3 to 4 controls. The Persian tricks in `taxonomy/techniques.json` apply unchanged.

### coding

- **Where the attack hides:** a code comment, a README, an issue or review comment, package metadata, a CI log or error message. New item kinds: `issue`, `review_comment`, `ci_log`. Code and manifests stay `file`.
- **What the attacker wants:** run a command that contacts the attacker (`run_command`), leak a secret through a link (`exfil_url`), change a CI file or add a dependency (new category `modify_code`).
- **The canary** sits in a private file the agent may read for its task, such as a local settings file.
- **New tools:** `read_issue`, `read_ci_log`, `edit_file`, `open_pr`.

### browsing

- **Where the attack hides:** a web page, a search-result snippet, a PDF. New item kind: `search_result`.
- **What the attacker wants:** open a link carrying the canary (`exfil_url`), submit a form (new category `submit_form`), or put a planted false claim into the answer (new category `misinform`, checked as text in `final_text`).
- **New tools:** `search_web`, `submit_form`.

### tool_output

- **Where the attack hides:** the description of a tool the runner registers, or the result that tool returns. New item kinds: `tool_description`, `tool_result`.
- **What the attacker wants:** the existing goals, such as leaking, sending, running or changing a setting.
- **No new tools:** the runner exposes one stub tool per case, named in the case.

## Schema and validator changes

- Add `profile` to the case schema and the new kinds, tools and goal categories to the enums and `taxonomy/tools.json`.
- Extend the reference-trace checks (V15, V16) to every new goal, so each check fires on the attacker's action and stays quiet on the user's task.
- Add rules for coding cases:
  - Dependency names are invented, and checks match only the name; a correct runner never installs anything.
  - CI edits are judged from `edit_file` arguments, never by running CI.

## Safety rules carried over

All rules in [authoring.md](authoring.md) still hold: invented people and companies, reserved hosts only, no working payloads, and commands that never run on a real machine. A dependency name could be registered on a public package registry by someone else, so runners must stub every install and network call.

## First real runs

No agent has been run against the set yet. For 0.2:

1. Run the full set against two open-source agents with a published tool mapping.
2. Publish the traces' scores with the dataset version, model and harness named.
3. Native speakers review all cases before the `0.1.0` and `0.2.0` tags.
