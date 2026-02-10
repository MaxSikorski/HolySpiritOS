# <img src="3logo.svg" width="40" align="center"> Verified ClawHub Automation ClawHub Stats Automation

This directory contains the logic used to power the live download counters for **HolySpiritOS**.

## 🧠 Technical Architecture: The "Hydration Pierce"

Standard scrapers fail on ClawHub because the download numbers are injected via **TanStack Router SSR** after the initial page load. 

### The Solution
Instead of looking for rendered HTML tags (which are empty when the bot visits), this workflow targets the `$_TSR.router` state object. 

1. **Identity Masking**: We use a high-authority Windows/Chrome User-Agent to ensure the server delivers the full JS payload rather than a bot-challenge page.
2. **Regex Targeting**: We use a Perl-Compatible Regular Expression (PCRE) to find the project metadata:
   `grep -oP '(?<=displayName":"HolySpiritOS").*?u":\K\d+'`
   - `(?<=...)`: Lookbehind to find your skill name.
   - `\K`: Discards the match history, keeping only the subsequent digits.
   - `\d+`: Captures the live download count.

### 24/7 Parallel Execution
The workflow is set to run hourly via GitHub Actions, ensuring your README reflects your growth without manual intervention.

### 🔧 The Components
* **Workflow:** [`.github/workflows/update_stats.yml`](../.github/workflows/update_stats.yml) - The agent that fetches the data.
* **Data Endpoint:** [`.github/data/stats.json`](../.github/data/stats.json) - The flat-file database used by Shields.io.

### 📝 Setup Guide
To use this for your own ClawHub skill:
1. Copy the `update_stats.yml` to your own repo.
2. Update the `curl` URL to your ClawHub profile.
3. Ensure your GitHub Actions have `Write` permissions in **Settings > Actions > General**.
4. Use this Markdown for your badge: 
`![Downloads](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/.github/data/stats.json&style=for-the-badge&color=orange)`
