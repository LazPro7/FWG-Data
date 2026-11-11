# Updating data.json

This is the instruction sheet for whoever (or whatever) refreshes the feed, including the scheduled routine.

## Naming (important)

The app must not use FIFA's protected names. In `data.json`, never write "FIFA" or "World Cup". Use:

| Source says | Write |
|---|---|
| FIFA | Football (as a name, e.g. "Football World Game 2030") or "football's governing body" (when it is the one acting, e.g. "Football's governing body hasn't published...") |
| World Cup | World Game |
| FIFA/Coca-Cola Men's World Ranking | official Men's Ranking |

Keep the existing names exactly, because the app matches them as text: "Football World Game 2030", "Football World Game 2026",
"Football Women's World Game 2027", "Football U-20 World Game 2027" and so on. Do not rename any JSON keys. Keys such as
`fifaRank` and `fifaRankingDate` stay as they are, because the app reads them by name.

Source names (FIFA.com and similar) may still be used when you *look up* facts. They must not appear in the data.

## Rules

1. Edit `data.json` only. Keep every existing key. Never rename or remove a key, and keep `schemaVersion` at `1`.
2. Only change a fact when a reliable source confirms it. Prefer FIFA.com, the confederations' own sites, and
   major news outlets. If sources disagree, keep the existing value or mark it "to be confirmed" in the text.
3. Never invent results, scores, dates, or qualified teams. When something is unknown, say so in the text.
4. Update `lastUpdated` (format `10 November 2026`) every time the data is checked, even if nothing else changed.
5. Run `python3 validate_feed.py data.json`. Only commit if it prints `OK`.

## What to check on every run

| Area | Where in data.json | What to look for |
|---|---|---|
| Men's World Game 2030 qualification | `confederations[].qualifiedTeams`, `confederations[].qualifyingStatus`, `teams[].qualified`, `mens.statTiles`, `mens.progressNote` | Newly qualified teams, qualifying start dates, FIFA's team-count decision (48 or 64), slot allocation |
| Men's schedule | `fixtures` | Draw date, published fixtures, final venue. Set `status` to `finished` and fill both scores once a match is played |
| FIFA men's ranking | `teams[].fifaRank`, `fifaRankingDate`, `mens.rankingExplainer` | A new monthly ranking release |
| Women's World Game 2027 | `competitions[id=women].next` | `qualified` and `qualifiedCount`, `status`, `keyDates` |
| U-20 World Game 2027 | `competitions[id=u20boys].next` | Same fields |
| U-20 Women's World Game 2028 | `competitions[id=u20girls].next` | Host and dates once announced |
| U-17 World Game 2026 | `competitions[id=u17boys]` | Match results during 19 Nov – 13 Dec 2026. When it ends, add the edition to `editions` |
| U-17 Women's World Game 2027 | `competitions[id=u17girls].next` | Dates, qualified teams |

## When a tournament finishes

1. Append a new object to that competition's `editions` (ascending year order): `year`, `host`, `champion`,
   `runnerUp`, `third`, `fourth`, `teams`, and `summary` (1–3 sentences, facts only).
2. Replace the competition's `results` with the final and third-place match from the new edition.
3. Replace `next` with the following edition. Reset `qualified` to `[]` and `qualifiedCount` to `0` until teams qualify.
4. Update `latestHeadline`.
5. For the men's World Game, also update `honours` (years for each nation), `appearances` (+1 for every team that played),
   `mens.championName`, `mens.championText`, and move the finished tournament's fixtures to `status: finished`.

## Publishing

Commit to the `main` branch. The app downloads the raw file at launch, when it returns to the foreground
(at most every 15 minutes), and on pull-to-refresh.
