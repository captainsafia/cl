# The Captain's Log

A minimal, automated weekly changelog site that aggregates open source contributions.

## Implementation Prompt

Use this prompt to recreate or adapt this project:

---

**Build a personal changelog website with the following specifications:**

### Overview
Create a static site that displays weekly summaries of GitHub contributions, automatically updated via GitHub Actions.

### Tech Stack
- **Frontend**: Vanilla HTML/JS with Tailwind CSS (via CDN)
- **Font**: JetBrains Mono (monospace)
- **Data**: Static JSON file (`data/changelog.json`)
- **Automation**: GitHub Actions workflow with AI summarization

### Data Structure

```json
{
  "weeks": [
    {
      "weekOf": "2026-01-19",
      "entries": [
        {
          "summary": "Human-readable description of the change",
          "repo": "owner/repo",
          "url": "https://github.com/owner/repo/commit/abc123"
        }
      ]
    }
  ]
}
```

**Important**: `weekOf` must always be a Monday (ISO format YYYY-MM-DD). Commits are bucketed by the Monday of their week (Mon-Sun).

### Frontend Features

1. **Infinite scroll** - Load 8 weeks at a time using IntersectionObserver
2. **Fade-in animation** - Entries animate in with opacity + translateY transition
3. **Week headers** - Display as "Week of [Month Day, Year]"
4. **Entry format** - Bullet list with summary text and linked repo name
5. **Responsive** - max-width container (4xl), horizontal padding

### Easter Egg
When hovering over a week header, convert the date to a Star Trek TNG-era stardate:
```javascript
stardate = (year - 2323) * 1000 + (dayOfYear / 365.25) * 1000
```

### GitHub Actions Workflow

**Trigger**: Weekly on Sunday at 11pm UTC + manual dispatch

**Steps**:
1. Fetch commits from the past week using GitHub API search:
   - Commits authored by the user in specified orgs/repos
   - Extract: date, repo, message, URL
2. Send commits to an AI agent with this prompt:
   ```
   Analyze the following Git commits and create a weekly changelog summary.
   
   Rules:
   - Generate MAX 5-7 bullet points total
   - Consolidate related changes into single bullets
   - Use concise, user-friendly language (no commit hashes or technical jargon)
   - Each bullet should describe the user-facing impact or purpose
   
   Output ONLY a valid JSON array:
   [{"summary": "...", "repo": "org/repo", "url": "https://..."}]
   ```
3. Calculate `weekOf` as the Monday of the current week: `date -d 'last monday' +%Y-%m-%d`
4. Merge new week into `changelog.json` (prepend or merge if week exists)
5. Commit and push changes

### Metadata
- Emoji favicon (📓) as SVG data URI
- OpenGraph tags for title, description, type, URL
- Twitter card metadata

### Style Guidelines
- Minimal, clean aesthetic
- Gray color palette (gray-400 for muted text, gray-700 for body)
- Subtle hover transitions on links
- Border-top separator for footer

---

## Local Development

Simply open `index.html` in a browser or serve with any static server:

```bash
python -m http.server 8000
```

## License

MIT
