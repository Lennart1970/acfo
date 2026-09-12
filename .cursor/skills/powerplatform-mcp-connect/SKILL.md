---
name: powerplatform-mcp-connect
description: >
  Connect Cursor (desktop or Cloud Agents) to Microsoft Power Platform via
  powerplatform-mcp-server (stdio, Azure CLI auth). Use when installing or
  repairing Power Platform / Power Automate MCP, wiring .cursor/mcp.json,
  running az login / device-code sign-in, --setup/--doctor, or when Power
  Platform tools are missing, unauthorized, or not listed on an agent run.
---

# Power Platform MCP connect

Get [`powerplatform-mcp-server`](https://www.npmjs.com/package/powerplatform-mcp-server) working with Cursor. Auth is **Azure CLI** (not Cursor marketplace OAuth). Default transport is **stdio**.

Pinned version used by this project: **`1.10.1`** (Node.js **`>= 22.19.0`**).

Upstream: [README](https://github.com/rcb0727/powerplatform-mcp-server) · [INSTALL](https://github.com/rcb0727/powerplatform-mcp-server/blob/main/INSTALL.md)

## When to use

- User asks to connect Power Platform / Power Automate / Dataverse MCP
- Agent run shows no `powerplatform` MCP namespace
- Tools fail with auth, consent, or “not signed in”
- Configuring Cloud Agents or local `.cursor/mcp.json`

## Prerequisites

- Node.js `>= 22.19`
- Azure CLI (`az`) available on the machine that runs the stdio server
- Microsoft 365 work account with Power Platform access
- Linux VMs: `libsecret` runtime if secure token storage is required by the package

Do **not** put Azure tokens or passwords in `environment.json`, git, or skill files.

## Path A — Desktop Cursor (local)

1. Install / refresh Azure CLI and sign in:
   ```bash
   az login
   az account show
   ```
2. One-shot setup (creates config + can wire Cursor):
   ```bash
   npx -y powerplatform-mcp-server@1.10.1 --setup --client cursor --npx
   ```
   Or configure manually in `~/.cursor/mcp.json` / project `.cursor/mcp.json`:
   ```json
   {
     "mcpServers": {
       "powerplatform": {
         "command": "npx",
         "args": ["-y", "powerplatform-mcp-server@1.10.1"]
       }
     }
   }
   ```
3. Confirm:
   ```bash
   npx -y powerplatform-mcp-server@1.10.1 --doctor
   ```
4. Restart Cursor. Ask the agent to list environments / flows.

Re-auth later without the wizard: `npx -y powerplatform-mcp-server@1.10.1 --login`, or call the server’s **`sign_in`** tool (device-code in chat).

## Path B — Cursor Cloud Agents (required for Project agents)

Cloud Agents **do not** load repo `.cursor/mcp.json`. A human must register the MCP in the Agents UI.

### B1. Add stdio MCP in the UI

1. Open [cursor.com/agents](https://cursor.com/agents).
2. **+** → **MCP Servers** → **Add MCP**.
3. Transport: **stdio**.
4. Rough config:
   - **Name:** `powerplatform` (or `powerplatform-mcp-server`)
   - **Command:** `npx`
   - **Args:** `-y` `powerplatform-mcp-server@1.10.1`
5. Enable the server for the run. Team plans may also add it under Dashboard → Integrations & MCP.

### B2. Make the Cloud Agent VM runnable

Stdio MCPs execute **inside** the agent VM. Ensure the Cloud Agent environment:

1. Uses Node `>= 22.19` (put the intended Node bin early on `PATH` if needed).
2. Can reach `registry.npmjs.org`.
3. Has Azure CLI installed (`az`).

Durable `install` sketch (review/Save on the environment dashboard — no secrets):

```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash || true
# Prefer a Node >= 22.19 toolchain for this package
```

### B3. Authenticate after the server is attached

1. Prefer the package **`sign_in`** tool (device-code flow in chat), **or** run `az login` / `powerplatform-mcp-server --login` in a session that can complete MFA.
2. Run setup once so config exists: `powerplatform-mcp-server --setup` (interactive TTY).
3. Confirm with `powerplatform-mcp-server --doctor`.

Until B1–B3 succeed, Project agents will keep showing **no Microsoft / Power Platform MCP**.

## Diagnosis cheatsheet

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| No Power Platform tools on Cloud Agent | MCP not added in Agents UI | Path B1 |
| `--doctor` / startup: missing config | Never ran setup | `--setup` in a TTY |
| Not signed in / token errors | No Azure CLI session | `az login`, `--login`, or `sign_in` |
| `AADSTS65001` / consent missing | Tenant consent gap | Entra admin consent — **do not** treat `--setup` as the fix |
| Tool missing from catalog | Tool set / profile excludes it | Re-run `--setup` and choose a profile that includes it |
| `403` on Dataverse / desktop flow / work queues | Missing Dynamics CRM delegated permission | Add + consent in Entra |
| Works on desktop, not in Cloud Agents | Only `.cursor/mcp.json` configured | Path B (UI registration) |

## Success criteria

- A Power Platform-related MCP namespace appears on the agent run.
- Environment / flow tools respond under the signed-in account.
- Auth remains Azure CLI / `sign_in` — not Cursor marketplace OAuth — for this package.

## Optional Microsoft-hosted alternative

If stdio + Azure CLI on the VM is too heavy, Microsoft’s hosted **Dataverse MCP** is HTTP + OAuth (`https://{org}.crm.dynamics.com/api/mcp`). That is a different tool surface than `powerplatform-mcp-server`. Use only if the tradeoff is accepted.
