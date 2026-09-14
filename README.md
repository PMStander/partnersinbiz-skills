# Partners in Biz skills

Public skill pack so **your** Cursor, Claude Code, or Hermes agent can operate a Partners in Biz workspace as **you**.

Repo: [github.com/Partners-in-Biz/partnersinbiz-skills](https://github.com/Partners-in-Biz/partnersinbiz-skills)

Admin and ops skills are included. The API still returns 403 when your membership cannot do the action. Do not use a platform god-key.

## Install

### Cursor

```bash
git clone https://github.com/Partners-in-Biz/partnersinbiz-skills.git ~/.cursor/skills/partnersinbiz-skills
# or: npx skills add Partners-in-Biz/partnersinbiz-skills
```

You can also clone into `~/.agents/skills/partnersinbiz-skills`.

### Claude Code

```bash
git clone https://github.com/Partners-in-Biz/partnersinbiz-skills.git ~/.claude/skills/partnersinbiz
```

### Hermes

```bash
git clone https://github.com/Partners-in-Biz/partnersinbiz-skills.git
cd partnersinbiz-skills
./bin/pib-skills install all
```

Default install target is `~/.hermes/skills`. Override with `PIB_SKILLS_DEST`.

## Sign in (required for API calls)

In-app Messages already injects a user token. External agents must log in:

```bash
./bin/pib-skills login
```

This opens Partners in Biz, you approve the agent, and credentials are stored at `~/.config/partnersinbiz/credentials.json`.

Headless fallback: Settings → Connected agents → Create personal token, then:

```bash
export PIB_ACCESS_TOKEN='pib_usr_…'
export PIB_ORG_ID='your-org-id'
```

Then call `GET https://partnersinbiz.online/api/v1/oauth/whoami` and send:

```
Authorization: Bearer <access token>
X-Org-Id: <orgId>
```

Never use `AI_API_KEY` for interactive work. That key is cron/system only.

## Layout

```
skills/*/SKILL.md   Agent Skills standard
manifest.json       Pack metadata
bin/pib-skills      install / login / status
docs/               auth notes (device OAuth + user-delegation)
```

Canonical source of truth for PiB fleet skill-packs is this repo, vendored into `partnersinbiz-web/packs/pib-system-skills` as a git submodule.

## Verify

```bash
./bin/pib-skills status
./bin/pib-skills whoami
```
