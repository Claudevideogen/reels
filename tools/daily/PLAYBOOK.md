# Daily Instagram reel — playbook

Goal: one well-made reel per day that reaches **business owners in the USA, Canada and Australia** who could buy
GoHighLevel (GHL) setup services — contractors and home services (HVAC, roofing, plumbing, electrical, cleaning,
landscaping), med spas, dentists, gyms, salons. The viewer must feel the problem, not feel sold to.

## Why the first reels got zero likes/comments/shares (Nov 18–24 diagnosis)
1. **Wrong time zone.** Posted 9–11 AM Pakistan = 11 PM–1 AM New York. Target audience asleep.
2. **Wrong first audience.** 75 followers / 266 following, mostly not target buyers; Instagram tests reels on them first.
3. **Wrong hashtags.** #GHL #GoHighLevel #AgencyOwner reach other agencies (competitors), not business owners.
4. **Felt like ads.** Brand named in the hook, prices, "comment LEADS", long disclaimers in caption.
5. **Niche jumps** (finance → GHL → entertainment) confuse the algorithm about who to show it to.
6. **No reason to interact.** No relatable/funny moment, no share prompt, no easy one-word question.
What worked: a first-person number hook ("40 leads. 3 booked.") cut 3-second skips from 67% to 32%.

## Non-negotiable rules
- Topic: GHL-solvable pain of a business owner (missed calls, slow replies, no-shows, no reviews, no follow-up,
  messy tools, dead leads, after-hours leads, rebooking, referrals). Speak to the owner, about their day.
- 22–30 s. Hook = number or POV in the first 2 s, money/pain consequence by ~3 s, re-hook ("Here's what…") at 10–12 s.
- Say "GoHighLevel" at most once, late, as the tool — never in the hook. No prices, no "DM me", no "comment X".
- American English, US dollars, US situations. Voice from `en-us` Kokoro voices (am_*/af_*).
- No made-up statistics. Use the viewer's own math ("At $500 a job, 3 missed calls = $1,500") or say "most".
- Every line gets its own matching shot. Cut 0.03 s before each line (render.py does this). Mark big moments `"hit": true`.
- Never repeat the previous reel's voice, music seed/bpm, or any clip id (check `log.md`). Vary the format.
- No game footage, no game sounds. No emoji inside rendered text (no emoji font).
- End with a **share** CTA ("Send this to a … who …") on the CTA card + spoken.
- The Pixabay key lives only in the GitHub secret. Never print, save or commit it.

## Formats to rotate (pick by weekday, don't repeat yesterday's)
- Mon — Money leak: number hook → cost → fix → share CTA.
- Tue — POV skit: "POV: you're a roofer and…" relatable/funny, fix at the end.
- Wed — One quick win: one automation explained in 3 steps.
- Thu — Myth vs reality / hot take ("Your ads aren't the problem.").
- Fri — Before/after day of an owner (hypothetical, clearly a scenario).
- Sat — Trend format adapted to owners (e.g. "Things contractors say that are lies").
- Sun — Checklist: "3 signs you're losing leads".

## Caption + posting
- Caption: hook line, 2–4 short lines of value, a soft line ("Save this for later"), then 5 hashtags max from:
  #smallbusinessowner #contractor #contractorlife #hvacbusiness #roofingcontractor #plumbingbusiness #homeservices
  #medspaowner #dentalpractice #salonowner #businesstips #leadgeneration (pick the 5 that match the reel). No #GHL.
- First comment: an easy one-word question ("What's your trade? 👇", "How many calls did you miss this week?").
- Schedule at **05:00 Asia/Karachi** (= 7 PM New York/Toronto, 4 PM LA, 11 AM Sydney). Metricool createScheduledPost:
  network instagram, media = raw GitHub URL, instagramData {type REEL, showReelOnFeed true, isAiGenerated true},
  firstCommentText, videoCoverMilliseconds at the hook label frame (~600 ms). Brand id 8193824, timezone Asia/Karachi.

## Pipeline (fresh session)
```bash
# repo: if /home/claude/reels missing -> add_repo Claudevideogen/reels (push) and clone there
cd /home/claude/reels && git fetch -q --depth 5 origin main && git reset -q --hard origin/main
bash tools/daily/setup.sh                       # deps + Kokoro model (~2 min first time)
# 1) write requests/<slug>.txt (one concrete visual query per script line), commit, push
git add requests && git -c user.name="Claudevideogen" -c user.email="358170666+Claudevideogen@users.noreply.github.com" commit -m "Request clips: <slug>" && git -c push.negotiate=true push origin main
# 2) wait for the Action (2–5 min):  gh run list -R Claudevideogen/reels -L 1
# 3) get clips from the throwaway branch
git fetch -q --depth 1 origin clips-<slug> && git checkout FETCH_HEAD -- clips/<slug> && git reset -q clips
python3 tools/daily/contact.py clips/<slug> /tmp/cs.png      # Read it; pick one clip per line (row NN, col a-d)
# 4) spec.json (see example below) in /home/claude/work/<slug>/ ; clip = filename without .mp4; cx = horizontal crop 0..1
python3 tools/daily/voice.py spec.json .  && python3 tools/daily/music.py spec.json .
python3 tools/daily/render.py spec.json . reel.mp4
python3 tools/daily/frames.py reel.mp4 /tmp/p.png <one time inside each line>   # Read it, fix crops/labels, re-render
ffmpeg -i reel.mp4 -vf "select='gt(scene,0.25)',showinfo" -f null - 2>&1 | grep -o 'pts_time:[0-9.]*'   # cuts == line starts
# 5) publish
cp reel.mp4 /home/claude/reels/videos/<YYYY-MM-DD>-<slug>.mp4 ; append log.md ; commit + push
#    URL: https://raw.githubusercontent.com/Claudevideogen/reels/main/videos/<file>.mp4 -> Metricool (see above)
rm -rf clips/<slug>   # (deleting the clips-<slug> branch is blocked from the session; leave it — the owner prunes them monthly)
```
Commit messages end with the Co-Authored-By / Claude-Session lines given by the session.

## spec.json example
See `tools/daily/examples/d1125-missed-calls.json`. Fields per line: `say` (spoken), `cap` (caption text if different,
e.g. "$1,500"), `label` (big pop text, short), `hit` (boom + flash on the cut), `hl` (words always yellow),
`clip`, `off` (start second in clip), `cx`/`cy` (crop 0..1), `gap` (pause before line). Top-level: `voices`,
`music` {bpm, root, mode, seed, energy}, `cta` (rows on the end card), `top` (optional header).
