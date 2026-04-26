# STT.ai MCP Server

Model Context Protocol server for [STT.ai](https://stt.ai). Lets Claude Desktop, Cursor, and any other MCP-compatible client transcribe audio/video, manage transcripts, and run AI features over them.

**Differentiator vs other STT MCP servers (Otter, Fireflies, Granola, Read AI):** those are read-only over stored transcripts. This one *also* exposes `transcribe_url` and `chat_with_transcript`, so Claude can transcribe a YouTube link and immediately query the result in one conversation.

## Tools

| Tool | What it does |
|---|---|
| `list_transcripts` | List your past transcripts (paginated, filter by status) |
| `get_transcript` | Fetch one transcript with segments, speakers, summary, metadata |
| `export_transcript` | Export as text/srt/vtt/json/csv |
| `transcribe_url` | Download + transcribe any URL (YouTube, podcast, direct file) |
| `summarize_transcript` | AI summary (cached or regenerated) |
| `analyze_transcript` | Sentiment, topics, entities, action items, questions, PII |
| `generate_from_transcript` | Blog posts, social media, study guides, flashcards, etc. |
| `chat_with_transcript` | RAG Q&A with source citations (segment IDs + timestamps) |
| `list_models` | Available transcription models with WER benchmarks |
| `list_languages` | Supported languages |

## Install

```bash
pip install sttai-mcp
```

## Configure

Get your STT.ai API key at https://stt.ai/account/#developer.

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "stt-ai": {
      "command": "sttai-mcp",
      "env": {
        "STT_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Restart Claude Desktop. The STT.ai tools should appear.

### Cursor

Settings → MCP → Add new MCP server:

```json
{
  "stt-ai": {
    "command": "sttai-mcp",
    "env": { "STT_API_KEY": "your-api-key-here" }
  }
}
```

### Run directly

```bash
STT_API_KEY=your-key sttai-mcp
```

The server speaks MCP over stdio.

## Examples

In Claude Desktop, after configuring:

> "Transcribe https://www.youtube.com/watch?v=dQw4w9WgXcQ and summarize the key points."

Claude will call `transcribe_url`, then `summarize_transcript` on the result.

> "What are my last 5 transcripts about?"

Claude calls `list_transcripts(limit=5)` and reads each title.

> "In transcript abc123, what did the speaker say about pricing?"

Claude calls `chat_with_transcript("abc123", "what did they say about pricing?")` and gets an answer with timestamped sources.

## Repo

- Source: https://github.com/sttaigit/sttai-mcp
- License: MIT
- Issues: https://github.com/sttaigit/sttai-mcp/issues

Maintained by [STT.ai](https://stt.ai).
