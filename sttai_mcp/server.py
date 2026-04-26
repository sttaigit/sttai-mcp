"""STT.ai MCP Server.

Exposes the STT.ai REST API as Model Context Protocol tools so Claude
Desktop, Cursor, or any other MCP-compatible client can transcribe URLs,
list and read past transcripts, summarize, analyze, generate content,
and chat with transcripts.

Differentiator vs every other STT MCP server (Otter, Fireflies, Granola,
Read AI as of 2026-04): those are read-only over stored transcripts;
this one ALSO offers `transcribe_url` and `chat_with_transcript`, so
Claude can transcribe a YouTube link and immediately query the result.

Auth: reads STT_API_KEY from environment. Get one at
https://stt.ai/account/#developer.
"""

from __future__ import annotations

import os
from typing import Optional

from mcp.server.fastmcp import FastMCP
from sttai import STTClient

mcp = FastMCP("STT.ai")


def _client() -> STTClient:
    """Lazy-construct the SDK client so the server starts cleanly even when
    STT_API_KEY is missing — only fails on the first tool call."""
    return STTClient(api_key=os.environ.get("STT_API_KEY"))


# ---------------------------------------------------------------------------
# Transcript management (read)
# ---------------------------------------------------------------------------

@mcp.tool()
def list_transcripts(limit: int = 20, offset: int = 0,
                     status: Optional[str] = None) -> dict:
    """List the user's transcripts.

    Args:
        limit: Max number to return (default 20, max ~100 per API).
        offset: Pagination offset.
        status: Filter by status — "completed", "processing", "failed", etc.
            None returns all.

    Returns:
        Pagination dict: {"results": [...], "count": int}.
    """
    return _client().list_transcripts(limit=limit, offset=offset, status=status)


@mcp.tool()
def get_transcript(transcript_id: str) -> dict:
    """Fetch a transcript by numeric ID or slug.

    Includes segments (with timestamps, speakers, text), summary if generated,
    duration, language, and metadata. Use this when the user asks "what did
    I say in transcript X" or wants to read/quote from a past transcript.
    """
    return _client().get_transcript(transcript_id)


@mcp.tool()
def export_transcript(transcript_id: str, fmt: str = "txt") -> str:
    """Export a transcript in a specific text format.

    Args:
        transcript_id: Numeric ID or slug.
        fmt: One of "txt", "srt", "vtt", "json", "csv". (Binary formats
            "docx" and "pdf" are not supported via this tool — use the
            web export instead.)

    Returns:
        The exported text content as a string.
    """
    if fmt in ("docx", "pdf"):
        raise ValueError(
            "Binary formats (docx, pdf) are not supported via MCP. "
            "Use the web export at https://stt.ai/transcripts/<slug>/."
        )
    result = _client().export_transcript(transcript_id, fmt=fmt)
    return result if isinstance(result, str) else str(result)


# ---------------------------------------------------------------------------
# Transcript creation (write — DIFFERENTIATOR vs read-only competitor MCPs)
# ---------------------------------------------------------------------------

@mcp.tool()
def transcribe_url(url: str, model: str = "large-v3-turbo",
                   language: str = "auto", diarize: bool = True,
                   speakers: int = 0) -> dict:
    """Download an audio/video file from a URL and transcribe it.

    Works with any publicly-accessible audio/video URL: direct file links,
    YouTube, podcast feeds, etc. Returns the full transcription including
    segments with speaker labels and timestamps.

    Args:
        url: URL of the audio/video to transcribe.
        model: Whisper model — "large-v3-turbo" (default, fast),
            "large-v3" (best accuracy), "stt-ai-enhanced" (paid plans only,
            our custom fine-tune), "nvidia-canary", "medium".
        language: ISO code (e.g. "en", "es") or "auto" for detection.
        diarize: Whether to identify and label distinct speakers.
        speakers: Expected number of speakers (0 = auto-detect).

    Returns:
        Transcription result: {"text": str, "segments": [...],
        "language": str, "duration": float}.
    """
    return _client().transcribe_url(
        url, model=model, language=language,
        diarize=diarize, speakers=speakers,
    )


# ---------------------------------------------------------------------------
# AI features over transcripts
# ---------------------------------------------------------------------------

@mcp.tool()
def summarize_transcript(transcript_id: str, force: bool = False) -> dict:
    """Get an AI summary of a stored transcript.

    Returns a cached summary if available; pass force=True to regenerate.
    Cheaper and faster than reading the full transcript when the user
    asks "what was that meeting about" or "summarize this lecture".
    """
    return _client().transcript_summarize(transcript_id, force=force)


@mcp.tool()
def analyze_transcript(transcript_id: str,
                       kinds: Optional[list[str]] = None) -> dict:
    """Run analysis on a transcript: sentiment, topics, entities, action
    items, questions, PII redaction.

    Args:
        transcript_id: Numeric ID or slug.
        kinds: List of kinds to run, or None for all. Valid kinds:
            "sentiment", "topics", "entities", "action_items",
            "questions", "pii".
    """
    return _client().transcript_analyze(transcript_id, kinds=kinds)


@mcp.tool()
def generate_from_transcript(transcript_id: str, kind: str,
                             prompt: Optional[str] = None) -> dict:
    """Generate derivative content from a transcript.

    Args:
        transcript_id: Numeric ID or slug.
        kind: What to generate. One of "blog_post", "social_twitter",
            "social_linkedin", "meeting_notes", "study_guide",
            "flashcards", "quiz", "newsletter", "podcast_show_notes".
        prompt: Optional custom instruction to steer the generation
            ("focus on the technical points", "make it under 280 chars", etc).

    Returns:
        {"content": str, ...}
    """
    return _client().transcript_generate(transcript_id, kind=kind, prompt=prompt)


@mcp.tool()
def chat_with_transcript(transcript_id: str, message: str,
                         session_id: Optional[str] = None) -> dict:
    """Ask a natural-language question about a transcript. Uses RAG with
    source citations — the response includes which segments backed each
    claim, so the user can verify by timestamp.

    Args:
        transcript_id: Numeric ID or slug.
        message: The question to ask.
        session_id: Optional, to maintain conversation context across
            multiple calls (the previous response includes a session_id
            you can pass here).

    Returns:
        {"answer": str, "sources": [{"segment_id": int, "text": str,
        "start_time": float}, ...], "session_id": str}.
    """
    return _client().transcript_chat(
        transcript_id, message=message, session_id=session_id,
    )


# ---------------------------------------------------------------------------
# Capability / health
# ---------------------------------------------------------------------------

@mcp.tool()
def list_models() -> dict:
    """List the available transcription models, with WER benchmarks and
    language support."""
    return _client().models()


@mcp.tool()
def list_languages() -> dict:
    """List the languages STT.ai supports for transcription."""
    return _client().languages()


def main() -> None:
    """Entry point for `sttai-mcp` console script."""
    mcp.run()


if __name__ == "__main__":
    main()
