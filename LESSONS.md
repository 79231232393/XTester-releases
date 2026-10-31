# Claude + Hermes: shared lessons

Living log of what we learned working together. Claude keeps this file in branch tg-stories.
Hermes adds lessons via status.json: `NOTE lesson: <text>`, and Claude copies them here with attribution.
Both sides read this before changing how they work.

## 2026-10-21
- (Hermes) Square copy must not contain unprovable claims ("most bots..."); animation must carry a large, readable "illustrative" label at phone size. → Claude: every Square video gets a permanent label and cautious copy.
- (Claude) Never change the queue while an item is in flight: removing 13-bossfight mid-run caused a 404. → Remove items only by new id / at prune time.
- (both) Feedback goes through status.json (Hermes → Claude) and note_from_claude (Claude → Hermes); Dmitrii only gets outcomes.

## 2026-10-25
- (Claude) New item types without a `video` field broke the sender ("ValueError"). → Schema 1 in FORMAT.md: kinds, optional fields, per-item errors, unknown kinds skipped with a reason.
- (Dmitrii) A skip is never the end state: say why and what is needed; Claude fixes and requeues until published.
- (Dmitrii) Telegram rule: only reels with 5000+ Instagram views, as a post with a link to the RU YouTube Short.
- (Hermes) The ValueError was his queue validation (queue_runtime.py validate → INVALID_FIELDS): a link item without kind/target/video blocked the whole queue. Hermes now quarantines per item and names item/stage/reason. He runs his own reviewed copy of tg_story.py + queue_runtime.py, not the upstream file.
- (Claude) Hermes is the source of truth for what his sender accepts. Send only fields from the agreed contract (FORMAT.md "Agreed with Hermes"), with explicit kind/target, plain-text post_text with the link inside, and no extra fields.
- (Hermes) If an item is unclear he asks about that item in status.json and holds only that item; Claude answers in note_from_claude, and a changed payload goes out under a new id.
- (Hermes) 25.10 04:00 installed telegram-queue/1.1-native-preview: YouTube preview is checked before sending and verified after. A missing or wrong preview holds the post, and nothing is resent when the result is uncertain.
- (Hermes) Every link post needs provenance in note_from_claude: the Instagram reel URL, the 5000+ view count with timestamp and source, the matching RU YouTube Short, and the owner's rule. Never invent numbers.
- (Hermes) 26.10: Binance Square rejected video post sq-13-bossfight-en-v2 with API 20013 "Content length is limited" at an 837-character caption. Keep Square video captions short (v3: 278 chars); Hermes reports the exact limit once observed. A rejected id is never replayed; the new version goes out as -vN.
- (Claude) 26.10: finished voiceover goes into the branch under audio/<id>/ with a manifest.json, and Claude removes the files once Hermes replies "received".
- (Claude) 27.10: Claude's shared project storage rewrites media files (mp4/wav/mp3) shortly after they are saved, so bytes and SHA256 change. Hashes are therefore always computed from the git checkout that gets pushed, never from shared storage. The V6 audio manifests were corrected in xtester-v6-ru-29s-audio-v2.
- (Hermes) 27.10: when the cloud cannot reach a host (xtester.pw), Hermes commits the files unchanged to a separate branch (yt-media) and Claude verifies the SHA256 from git. It worked first time for XTESTER-YOUTUBE-RU-EN-PUBLISH-20261027.
