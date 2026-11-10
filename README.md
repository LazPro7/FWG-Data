# Football World Game data feed

`data.json` is the live data for the Football World Game app. The app downloads it, checks it, and falls back
to its built-in copy if the download fails or the file is invalid.

## One-time setup

1. Create a GitHub repository (public, so the app can read it without a login) and push this folder to it.
2. Open `data.json` on GitHub and click **Raw**. Copy the address, which looks like
   `https://raw.githubusercontent.com/<you>/<repo>/main/data.json`.
3. In the app project, open `MyApp/DataStore.swift` and paste it into `DataStore.feedURLString`.
4. Build and run. The footer of every screen shows "Live feed" once the download works.

## Files

| File | Purpose |
|---|---|
| `data.json` | The feed the app reads |
| `validate_feed.py` | Checks the feed's structure and consistency. The GitHub workflow runs it on every change |
| `UPDATING.md` | Rules and a checklist for updating the data |
| `.github/workflows/validate.yml` | Blocks a broken feed from being merged unnoticed |

## Regenerating the starting file from the app's built-in data

The built-in data lives in `MyApp/Models.swift`, `Competitions.swift`, `BundledMatches.swift` and `AppData.swift`.
If you change its structure, regenerate `data.json` from those files and keep `schemaVersion` in step with
`AppData.supportedSchemaVersion`.
