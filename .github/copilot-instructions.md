# Copilot Instructions for EPIRef PDF Report Listing

## Project Overview
- **Purpose:** This project provides a web-based index of occupational disease epidemiology reports (PDFs) for easy browsing and access.
- **Main Components:**
  - `index.html`: The only code file, containing all HTML, CSS, and JavaScript for the UI and logic.
  - `docs/`: Directory containing all PDF files, named in a consistent pattern (e.g., `koshaYYYY_NNN_NNN.pdf`).

## Data Flow & Architecture
- The web app is static and client-side only. There is no backend.
- On page load, JavaScript fetches the list of PDFs from the GitHub repository using the GitHub REST API (`/repos/:owner/:repo/contents/docs`).
- The list is filtered for `.pdf` files, sorted alphabetically, and rendered as a styled list with links to the raw files on GitHub Pages.
- All PDF links use the GitHub Pages URL pattern: `https://jinhaslab.github.io/epiref/docs/<filename>.pdf`.

## Key Patterns & Conventions
- **No build step:** All logic is in `index.html`. No npm, package.json, or build tools are used.
- **No tests or CI:** There are no automated tests or CI/CD scripts.
- **PDF file naming:** All PDFs follow a `koshaYYYY_NNN_NNN.pdf` or similar pattern for easy sorting and recognition.
- **Error handling:** If the GitHub API fails, a user-friendly error message is shown in Korean.
- **UI/UX:** Modern, clean, and responsive design using embedded CSS. SVG icons are used for file links.
- **Language:** Korean is used for all user-facing text.

## Developer Workflows
- **To add new PDFs:** Place new files in the `docs/` directory. No code changes are needed; the list updates automatically.
- **To update the UI/logic:** Edit `index.html` directly. All code is in this file.
- **To preview locally:** Open `index.html` in a browser. For full functionality (API fetch), deploy to GitHub Pages or use a local server with CORS enabled.

## Integration Points
- **GitHub API:** Used to fetch the file list. No authentication is required for public repos, but rate limits apply.
- **GitHub Pages:** Used to serve the PDFs and the web UI.

## Examples
- To add a new report: `docs/kosha2025_001_002.pdf` (no code change needed).
- To change the UI: Edit the `<style>` or JavaScript in `index.html`.

## Special Notes
- Do not add build tools, frameworks, or extra dependencies unless explicitly requested.
- Keep all logic in `index.html` unless the project structure changes.
- Maintain Korean language for all user-facing content.

---
_Last updated: 2025-07-25_
