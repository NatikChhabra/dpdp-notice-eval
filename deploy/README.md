# Deploying the demo to Hugging Face Spaces

The Space holds only the three files in `space/`. It installs this repo from GitHub at a pinned commit.
To update it, push to `main`, then change the commit in the Space's `requirements.txt` (a plain restart
reuses the cached install).

1. Create a Gradio Space named `dpdp-notice-check`.
2. Add `space/README.md`, `space/requirements.txt` and `space/app.py` to it.
3. In the Space's **Settings → Variables and secrets**, add the secret `GEMINI_API_KEY`. Without it the
   demo uses the keyword baseline and says so.
4. Optional variable `DPDP_JUDGE_MODELS` (comma-separated, first one tried first).
