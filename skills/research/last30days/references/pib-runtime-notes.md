# PiB runtime notes for last30days

Source: https://github.com/mvanhorn/last30days-skill
Imported commit: 122158415ae4

Use this skill for recent public-market/community research only. It is not a substitute for PiB tenant-scoped client records.

PiB boundaries:
- Resolve the client workspace and orgId before mixing findings with client data.
- Do not ingest private client documents, CRM exports, mailbox content, or credentials into the skill engine unless Peet has approved the exact client scope.
- Optional API keys listed by the upstream skill are not to be requested in chat or pasted into notes. Use profile-managed environment variables only when already configured.
- If the engine cannot access a source, report the unavailable source rather than fabricating coverage.
