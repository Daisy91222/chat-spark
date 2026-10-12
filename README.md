# Chat Spark

A Codex desktop skill that adds QQ-inspired activity badges to ChatGPT and Codex chat titles.

- User activity on 3, 7, or 30 consecutive days earns 🔥, 🔥🔥, or 🔥🔥🔥.
- Being the unique chat with the most completed question–answer rounds for 7 consecutive days earns ⛵️; 30 days upgrades it to 🚢.
- The first version considers the 50 most recent chats plus pinned chats that the Codex desktop tools can read.

## Install and use

Copy this directory to your Codex skills directory as `chat-spark`, then invoke `$chat-spark` in a Codex desktop chat. The skill needs the desktop app's `list_threads`, `read_thread`, and `set_thread_title` tools. It does not access ChatGPT history through the OpenAI API.

Choose a persistent writable state file outside this repository, for example a `work/chat-spark-state.json` file in a personal workspace. Use the same state path every time, including in any daily scheduled task. The skill keeps daily counts and title markers there; it does not save message bodies.

Schedule a daily task for 09:00 in your local time zone and ask it to run `$chat-spark` against the prior complete day. Review the first run before relying on the schedule.

The scorer is `scripts/score.py`. Its `plan` command proposes title changes from an aggregated snapshot, and `commit` records which title changes succeeded.
