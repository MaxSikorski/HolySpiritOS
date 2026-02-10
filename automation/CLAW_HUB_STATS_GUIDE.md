# <img src="2logo.svg" width="40" align="center"> Verified ClawHub Automation ClawHub Stats Automation

This directory contains the logic used to power the live download counters for **HolySpiritOS**.

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
