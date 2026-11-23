# Queue format, schema 1 (proposal from Claude, 25.10.2026)

`queue.json` = `{"schema": 1, "items": [ ... ]}`. One item = one task. Every reader must follow these rules:

1. **Unknown fields are ignored.** New optional fields can appear at any time.
2. **Unknown `kind`, unknown `target` or `schema` > supported** → skip the item, log `NOTE <id>: skipped, unknown kind <kind>`, continue. Never crash the whole run.
3. **Missing field required for its kind** → log `FAIL <id>: missing <field>`, skip, continue.
4. `id` is unique and never reused. A fix comes as a new id (`-v2`, `-v3`), and the old one is removed.
5. One bad item must never block the others. Wrap each item in its own try/except.

| kind | target | required | optional |
|---|---|---|---|
| `story_video` | telegram | `video` | `caption`, `period_hours` (default 24), `pinned`, `also_post`, `post_text` |
| `link_post` | telegram | `link`, `post_text` | `caption` (same text) |
| `square_video` | binance_square | `video`, `caption` | `qa_sheet` |
| `diagnostic` | hermes | `note_from_claude` | — (a message or task for Hermes, never published) |

Common optional fields: `note_from_claude`, `added`, `added_ts`, `qa_sheet`.
Legacy items without `kind`: `link` present → `link_post`; `target`=binance_square → `square_video`; otherwise `story_video`.
`video`, `qa_sheet` are paths relative to the branch root (raw URL = https://raw.githubusercontent.com/79231232393/XTester-releases/tg-stories/<path>).

Status (`status.json`, branch tg-status): `done[id]` = `{"at", "story", "post", "square"}` (null when n/a);
`log` lines start with `OK <id>`, `FAIL <id>`, `NOTE <id>` or `NOTE:`. Questions or objections to Claude go into `log` as `NOTE <id>: ...`.
To agree or propose changes to this format, write `NOTE format: ACCEPT schema 1` or `NOTE format: <change>`.

## A skip is a signal, not an end state (Dmitrii, 25.10)
Every task must end up done. A `NOTE <id>: skipped` or a `FAIL <id>` must say **why** and **what you need**
(e.g. `NOTE x: skipped, unknown kind poll; need: instructions for poll`). Claude reads it, fixes the task or teaches
the new kind here with an example, and requeues it under a new id until it is published. Don't silently drop tasks.

## Examples
```json
{"id": "29-survivorship-tg", "kind": "link_post", "target": "telegram",
 "link": "https://youtube.com/shorts/XXXX", "post_text": "**Hook** ...\n\nBody ...\n\nQuestion 👇"}
{"id": "42-round3", "kind": "story_video", "target": "telegram", "video": "videos/42-round3.mp4",
 "caption": "≤200 chars", "period_hours": 24, "also_post": true, "post_text": "..."}
{"id": "sq-13-bossfight-en-v2", "kind": "square_video", "target": "binance_square",
 "video": "videos/sq-13-bossfight-en-v2.mp4", "caption": "full EN post, no links", "qa_sheet": "qa/sq-13-bossfight-en-v2.jpg"}
{"id": "diag-1", "kind": "diagnostic", "target": "hermes", "note_from_claude": "question or task for Hermes"}
```

## Agreed with Hermes (25.10.2026, his NOTE format replies) — this overrides the proposal above where they differ
- Envelope `{"schema":1,"items":[...]}`; items may carry `schema_version: 1`. Explicit `kind` and `target` on every new item.
- Telegram kinds: `story_video`, `text_post`, `link_post`. Unknown/invalid → QUARANTINED_NOT_SENT for that item only; siblings continue.
- Unknown publication fields are NOT ignored (they quarantine the item). Claude sends only the documented fields.
- `link_post`: fields id, kind, target, link (HTTPS), post_text (plain text, no Markdown, ≤4096 UTF-16, link already inside verbatim), `link_preview`.
  Dmitrii wants the YouTube preview: `link_preview: true` is REQUIRED for our link posts; Hermes holds them until preview support is in.
- `story_video`: videos/<name>.mp4, portrait ≤60 s, RU caption ≤1024 with xtester.pw/copytrader.pw CTA; 24 h story, pinned=false, also_post=false by default.
- Duplicate ids hold; a changed payload needs a new id; ids are never reused.
- Hermes asks item-specific questions in status.json; Claude answers in `note_from_claude`; the item waits only for that answer.
