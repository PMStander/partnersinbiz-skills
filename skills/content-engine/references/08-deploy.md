# Phase 8 — Deploy (GitHub + Vercel)

The preview site is deployed two ways simultaneously: a private GitHub repo for version control + change tracking, and a Vercel production URL the client can actually open.

## Prerequisites

```bash
which gh && gh auth status   # logged in to GitHub
which vercel && vercel whoami # logged in to Vercel
```

If either is missing, the user needs to set them up first. Don't try to deploy with broken auth.

## Step 1 — Initialize git in the preview folder

```bash
cd <workspace>/marketing/preview
cat > .gitignore <<'EOF'
.DS_Store
node_modules
.vercel
*.log
EOF
git init -q
git add .
git commit -qm "Initial commit: [Client] marketing preview ([Month Year])"
```

## Step 2 — Create private GitHub repo

```bash
gh repo create [client-slug]-marketing-preview \
  --private \
  --source=. \
  --description "[Client] marketing preview (passcode-protected client review site)" \
  --push
```

The `--push` flag pushes the initial commit immediately. If the user prefers their own GitHub org, add `--owner [org-name]`.

## Step 3 — Link to a NEW Vercel project (one per client — critical)

Each client MUST get their own Vercel project. NEVER reuse the "preview" project or any other client's project — they overwrite each other.

Get the team scope once: `vercel teams list`. On a personal account use your username.

```bash
cd <workspace>/marketing/preview

# Delete any existing .vercel link (forces creation of a new project)
rm -f .vercel/project.json

# Link to a new named project — this creates it if it doesn't exist
vercel link --scope [team-scope] --project [client-slug]-marketing-preview --yes

# Deploy to production
vercel --prod --yes --scope [team-scope]
```

The clean production URL will be:
```
https://[client-slug]-marketing-preview.vercel.app
```

Note the URL and project ID from the deploy output.

## Step 4 — Disable Vercel deployment protection (CRITICAL)

By default, Vercel team accounts add SSO protection — the URL returns 401 to anyone without team access. You MUST disable this for the client to be able to view the site. The 5566 passcode is your gate.

```bash
# Get the Vercel auth token
VERCEL_TOKEN=$(find ~/Library/Application\ Support/com.vercel.cli ~/.config/vercel ~/.vercel 2>/dev/null \
  -name "auth.json" -exec cat {} \; 2>/dev/null \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('token',''))" 2>/dev/null)

# Get the project ID from .vercel/project.json
PROJECT_ID=$(python3 -c "import json; print(json.load(open('.vercel/project.json'))['projectId'])")
TEAM_ID=$(python3 -c "import json; print(json.load(open('.vercel/project.json'))['orgId'])")

# Disable both SSO and password protection (the 5566 passcode is enough)
curl -s -X PATCH "https://api.vercel.com/v9/projects/${PROJECT_ID}?teamId=${TEAM_ID}" \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ssoProtection":null,"passwordProtection":null}' | head -c 200
```

After this runs, the URL becomes publicly accessible. The 5566 passcode in the HTML is now the only gate (plus `X-Robots-Tag: noindex` from `vercel.json`).

## Step 5 — Optional: rename the project for a cleaner URL

The default URL will be something like `preview-xi-two.vercel.app`. To get `[client-slug]-marketing-preview.vercel.app`:

```bash
curl -s -X PATCH "https://api.vercel.com/v9/projects/${PROJECT_ID}?teamId=${TEAM_ID}" \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"[client-slug]-marketing-preview"}'

# Redeploy to refresh aliases
vercel deploy --prod --yes --scope [team-scope]
```

## Step 6 — Verify end-to-end

```bash
URL="https://[your-final-url]"
curl -s -o /dev/null -w "HTML: %{http_code}\n" "$URL"
curl -s -o /dev/null -w "image: %{http_code}\n" "$URL/assets/images/B1-fill-in.png"
curl -s -o /dev/null -w "video: %{http_code}\n" "$URL/assets/videos/V1-fill-in/"
```

All three should be 200. Note: videos are served as HTML directories, not .mp4 files. If any are 401, the deployment protection didn't disable — re-run Step 4.

## Step 7 — Hand it off to the user

Give the user three things:
1. **Live URL** for the client
2. **Passcode** (`5566` unless changed)
3. **GitHub repo URL** (for version control / change tracking)

Plus instructions for the rebuild + redeploy cycle:
```bash
cd <workspace>/marketing/preview
python3 build.py                       # rebuild after content edits
git add . && git commit -m "Update content" && git push
vercel --prod --yes --scope [team-scope]
```

Whole rebuild + redeploy cycle is < 90 seconds.

## Optional: custom domain

If the client wants `marketing.[client-domain].com` instead of the .vercel.app URL:

```bash
# Add the domain to the project
vercel domains add marketing.[client-domain].com
# Vercel will print DNS records to add
```

The user adds the DNS record in their registrar; Vercel auto-provisions the SSL cert. Takes 5–10 min to propagate.

## Common deploy issues (from real production)

| Issue | Fix |
|---|---|
| `vercel --prod` returns 401 even after deploy | SSO protection still on — re-run Step 4 |
| Vercel CLI: "missing scope" in non-interactive mode | Add `--scope [team-id]` to every command |
| Renaming project doesn't change URL | Need to redeploy after renaming for aliases to update |
| Wrong project gets the deploy | `cat .vercel/project.json` to confirm — re-link with `vercel link` if wrong |
| Asset 404s (videos/images) | The deploy didn't upload `assets/` folder — check `.vercelignore` doesn't exclude it |
| Custom domain stays at "pending verification" | Wait 5–10 min, run `vercel domains inspect <domain>` to see DNS status |

## Time budget

Phase 8 should take **10–15 minutes**:
- Git init + commit + push to GitHub: 2 min
- Vercel first deploy: 2 min
- Disable protection + verify: 3 min
- (Optional) rename + redeploy: 3 min
- Hand-off message to user: 2 min
