#!/usr/bin/env python3
import asyncio
import re
import subprocess
from pathlib import Path

import edge_tts
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts" / "demo-video"
OUT.mkdir(parents=True, exist_ok=True)

SCRIPT = """Prize hunting sounds simple until you actually try to do it.

Every contest, bounty, grant, and hackathon has different deadlines, rules, eligibility limits, prize terms, intellectual property language, tax notes, and restrictions on AI or automation.

PrizePilot turns that messy chore into a structured, human in the loop workflow.

This is not an auto submit bot. PrizePilot helps research, evaluate, plan, draft, and prepare materials, while keeping the user responsible for final review and submission.

Here is the live PrizePilot app running on Google Cloud Run.

The dashboard starts with ranked opportunities. The primary target is the All Things Agentic Hackathon, but the fixture set also includes ARC Prize 2026, Agentic Cinema, Agents for Humans, and a sample security bounty marked blocked until official scope and safe harbor are verified.

Each opportunity tracks status, deadline, prize value, expected value, risk level, and the recommended next action.

Opening the All Things Agentic opportunity shows the full workflow.

First, the intake record captures the sponsor, official URL, prize, deliverables, submission method, automation restrictions, IP terms, tax notes, and source notes. Anything that has not been verified stays marked as needing verification.

Next is the Rules Extractor. I paste a short rules excerpt and ask PrizePilot to extract a structured summary.

The backend uses the Google GenAI SDK with Gemini through Vertex AI on Cloud Run. It returns eligibility items, deliverables, deadlines, AI use notes, automation notes, IP terms, fees, tax notes, risk flags, and unknown items to verify.

Now I score the opportunity.

PrizePilot uses the required expected value model: prize value, probability of success, skill fit, effort required, deadline urgency, rule clarity and safety, reusability, and automation suitability. Each category gets a score from one to ten, with a plain English explanation, and the final weighted score is shown from zero to one hundred.

Next, I generate a Win Plan.

The plan turns the opportunity into an execution checklist: why it is worth pursuing, rules summary, eligibility checklist, submission checklist, judging criteria breakdown, best strategy, differentiation angle, required research, deliverables, timeline, risks, compliance notes, sources needed, and final review checklist.

Then the Drafting Assistant creates review only materials. Drafts include assumptions, claims needing verification, missing user inputs, and a final review checklist. They are deliberately not final submissions.

The most important safety moment is the Compliance Gatekeeper.

If I ask PrizePilot to automatically submit the entry and accept terms for me, it refuses. The action is blocked, and the app says: This action requires explicit human approval and must be completed manually outside PrizePilot.

That same gate also flags fake credentials, fake nonprofit claims, fake citations, unsupported impact claims, payments, tax documents, sensitive personal data, unauthorized security testing, out of scope bounty work, IP ambiguity, and rules that appear to ban AI or automation.

Finally, here is the Google Cloud proof.

The health endpoint reports Cloud Run, Firestore storage, Gemini through the Google GenAI SDK and Vertex AI, and the configured Gemini model. Cloud Run logs show live requests to the deployed app.

PrizePilot is a complete workflow agent for the Taskmaster track: it takes a messy multi step chore and turns it into a scored, planned, compliance checked submission workflow.

The human stays in control. PrizePilot prepares the work. The user reviews, approves, and submits manually outside the app."""


def chunks(text: str) -> list[str]:
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    output: list[str] = []
    for paragraph in paragraphs:
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        current = ""
        for sentence in sentences:
            candidate = f"{current} {sentence}".strip()
            if len(candidate) <= 260:
                current = candidate
            else:
                if current:
                    output.append(current)
                current = sentence
        if current:
            output.append(current)
    return output


async def synthesize_chunk(text: str, path: Path, voice: str) -> None:
    last_error: Exception | None = None
    for attempt in range(1, 4):
        if path.exists():
            path.unlink()
        try:
            communicate = edge_tts.Communicate(
                text,
                voice=voice,
                rate="+6%",
                volume="+0%",
                pitch="+0Hz",
            )
            await communicate.save(str(path))
            if path.exists() and path.stat().st_size > 0:
                return
        except Exception as exc:
            last_error = exc
            await asyncio.sleep(1.5 * attempt)
    raise RuntimeError(f"Edge TTS failed for chunk: {text[:80]!r}") from last_error


async def main() -> None:
    script_path = OUT / "voiceover-script.txt"
    audio_path = OUT / "voiceover.mp3"
    script_path.write_text(SCRIPT + "\n")

    voice = "en-US-JennyNeural"
    chunk_paths: list[Path] = []
    for stale in OUT.glob("voiceover-chunk-*.mp3"):
        stale.unlink()
    for index, chunk in enumerate(chunks(SCRIPT), start=1):
        chunk_path = OUT / f"voiceover-chunk-{index:02d}.mp3"
        await synthesize_chunk(chunk, chunk_path, voice)
        chunk_paths.append(chunk_path)

    concat_file = OUT / "voiceover-concat.txt"
    concat_file.write_text("".join(f"file '{path.name}'\n" for path in chunk_paths))
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(audio_path),
        ],
        cwd=OUT,
        check=True,
    )
    print(audio_path)


if __name__ == "__main__":
    asyncio.run(main())
