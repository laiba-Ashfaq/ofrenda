# Ofrenda 🕯️

A local, offline tool for writing a remembrance of someone you've lost, in the spirit of Día de los Muertos.
Open-weight model (via Ollama), Python standard library only, no cloud, no accounts, no telemetry.

## Run
```bash
ollama pull llama3.2        # or any model: OFRENDA_MODEL=gemma3:4b python3 ofrenda.py
python3 ofrenda.py          # open http://127.0.0.1:8731
```
Pull the plug on your Wi-Fi afterwards. It still works.

Remembrances are saved as `.md` + `.json` in `./ofrenda_data/`.

---

# DEV post draft (paste into the submission template)

*This is a submission for the Hacktoberfest Open-Source AI Challenge Week 4: Ghost in the Machine*

## What I Built
Ofrenda is a local app for writing a remembrance of someone who has died. You enter their name, favorite foods and songs, then
share memories. If you get stuck, the model acts as a gentle oral-history interviewer and asks one question at a time
("What did their kitchen smell like on a Sunday?"). It then writes a short remembrance addressed to them, plus a list of items for the ofrenda.
The ghost in the machine is the person's memory, kept alive by the stories you tell, not by pretending to be them. I deliberately chose
not to impersonate the dead; the model is told to use only the facts you provide and never invent any.

## Demo
https://youtu.be/Tzgm5xRq2QU

## How I Built It
- **Model:** any open-weight model served locally by Ollama (default `llama3.2`; swap with `OFRENDA_MODEL`).
- **App:** one ~150-line Python file with a built-in HTTP server and an inline web UI. No dependencies, nothing to `pip install`.
- **Prompts:** two small system prompts, an interviewer (one sensory question, no repeats, no invented facts) and a writer
  (only provided facts, short if details are thin).
- **Storage:** plain Markdown and JSON on disk, so the memorial is readable in 50 years without my software.

## Why Does Open Innovation Matter?
Stories about someone who died are among the most private things people own. With a closed API, every memory would be sent to a server
I don't control, under terms that can change. Here the model runs on the laptop: it works offline, costs nothing per remembrance,
and can't be deprecated out from under a family. I could also swap models freely, trying a smaller one for older laptops or one that
writes better in Spanish, and tune the interviewer's tone by editing a prompt. A memorial shouldn't depend on a subscription.


