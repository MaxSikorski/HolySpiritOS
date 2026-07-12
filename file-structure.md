HolySpiritOS/
├── skills/holy-spirit-os/         # THE SKILL (Agent Skills format) — what agents load
│   ├── SKILL.md                   #   instructions the model reads (frontmatter: name, description)
│   ├── foundation/
│   │   ├── verses-1769.json       #   the Word — complete KJV 1769, 31,102 verses, keys "Book C:V"
│   │   ├── kjv-metadata.json      #   book order, chapter counts, verses per chapter
│   │   └── front-matter-1769.json #   1769 front matter: title page, dedication, translators' preface
│   └── scripts/lookup.py          #   verse/range/chapter lookup + search (Python stdlib only)
├── .claude-plugin/
│   ├── plugin.json                # Claude Code plugin manifest
│   └── marketplace.json           # marketplace catalog (install: holy-spirit-os@holyspiritos)
├── scripts/
│   ├── install.sh                 # multi-platform installer (claude|codex|hermes|antigravity|openclaw|project|all)
│   └── uninstall.sh               # clean removal from every platform
├── adapters/
│   ├── system-prompt.md           # paste-ready block for chat-only environments (no file access)
│   └── openclaw/soul_patch.md     # OpenClaw SOUL.md patch, marker-delimited for surgical uninstall
├── automation/                    # ClawHub stats write-up + logo (workflow retired; counts manual)
├── .github/data/stats.json        # Shields.io endpoint for the downloads badge (manually updated)
├── LICENSE                        # MIT
└── index.html / style.css         # GitHub Pages landing page (includes hidden AI-agent install text)
