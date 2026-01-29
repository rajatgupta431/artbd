# Art Board Server - Self-Contained Executable Builder

Creates a single Windows `.exe` that has your art board files **embedded inside** — nothing else to distribute.

## Setup

```
your-repo/
├── .github/
│   └── workflows/
│       └── build.yml
├── art_board_server.py
├── static_files/          <-- PUT YOUR BUILT FILES HERE
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── assets/
│       └── ...
└── README.md
```

## How to Build

1. **Copy your built art board files** into the `static_files/` folder
2. **Push to GitHub**
3. Go to **Actions** tab → wait for build to complete
4. **Download** the `ArtBoardServer-Windows` artifact
5. Extract to get `ArtBoardServer.exe`

## Distribution

Just share the single `ArtBoardServer.exe` file. When someone runs it:
- A local server starts automatically
- Their browser opens to view your art board
- All files are embedded in the exe — nothing to extract

## Local Testing (Mac)

To test locally on Mac before pushing:

```bash
pip install pyinstaller

# Put your files in static_files/ folder, then:
pyinstaller --onefile --name ArtBoardServer --add-data "static_files:static_files" art_board_server.py

# Run it
./dist/ArtBoardServer
```

## Notes

- The exe extracts files to a temp folder at runtime and cleans up on exit
- Default port is 8080 — edit `art_board_server.py` to change
- Files are embedded but not encrypted — this hides them from casual users but isn't DRM
