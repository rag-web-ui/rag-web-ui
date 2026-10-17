# Build a knowledge base from web sources

Use [Parallel Search MCP](https://docs.parallel.ai/integrations/mcp/search-mcp)
in VS Code to find public web pages, then turn selected material into a reviewed
Markdown document for RAG Web UI. This is useful for a small research collection,
such as documentation about a library you are learning.

Parallel provides free web search and page fetching without a Parallel account or
API key. Anonymous searches use Fast mode and have lower rate limits. This guide
uses an external MCP client to prepare files; RAG Web UI answers from the files
you upload. The uploaded content is a snapshot, so refresh it when sources change.

## 1. Configure Parallel in VS Code

You need a working [RAG Web UI installation](../README.md#-quick-start), plus
VS Code with an MCP-capable chat agent configured. Your chat agent's own access
requirements still apply.

Run **MCP: Open User Configuration** from the VS Code Command Palette. Merge this
entry into the existing `servers` object in your user-profile `mcp.json`, keeping
any other servers:

```json
{
  "servers": {
    "parallel-search": {
      "type": "http",
      "url": "https://search.parallel.ai/mcp",
      "headers": {
        "User-Agent": "rag-web-ui-web-sources/1.0"
      }
    }
  }
}
```

Start the server using **MCP: List Servers**, accept the trust prompt if shown,
and open chat. In **Configure Tools**, enable Parallel's `web_search` and
`web_fetch` tools. See [VS Code's MCP setup guide](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
for server controls and troubleshooting. No RAG Web UI environment variables or
provider changes are needed.

## 2. Research and review a small collection

For example, ask your VS Code chat agent:

```text
Use Parallel web_search to find the official Ollama documentation about embedding
models. Use web_fetch to read the relevant pages. Draft a short Markdown research
note explaining how to choose an embedding model. For each source, include its
page title, full source URL as plain text, and the date you fetched it. Separate
facts from recommendations, and report any page you could not fetch. Do not
include claims based only on a search snippet.
```

Inspect the tool results and open the original pages to check the draft. Fetching
can fail or return partial content; omit unsupported claims. Keep the collection
focused, and include only content you have permission to store. If the service
reports a rate limit, wait for its indicated retry time rather than repeatedly
submitting the same request.

Save your reviewed notes as a UTF-8 file, for example `embedding-research.md`.
Use a short section per source, with the URL and retrieval date in the text:

```markdown
# Embedding model research

## Source: <page title>
Source URL: <full URL of the page you read>
Retrieved (UTC): <YYYY-MM-DD>

<Verified facts or a short excerpt, with enough context to understand it.>
```

Replace the placeholders before uploading. Plain-text URLs keep provenance in
the document body even when Markdown formatting is removed during ingestion.
Keep source details near the material they describe, and check the chunk preview
to see whether they remain together.

## 3. Upload, check retrieval, and chat

1. Open or create a knowledge base in RAG Web UI, then select **Add Document**.
2. Select your `.md` file and choose **Upload Files**.
3. In the preview step, keep the default chunk settings, choose the document,
   and select **Preview Chunks**. Check that the text, source URLs, and dates are
   present. The preview's chunk settings do not change final processing. If
   important context is separated, shorten or split your notes and upload the
   revised file.
4. Select **Continue**, then **Process**, and wait for processing to complete
   successfully.
5. From the knowledge-base list, open the retrieval test using that knowledge
   base's search icon. Ask a question whose answer appears in your notes and
   inspect the returned chunks. If the expected text is absent, check processing
   status and the chunk preview before starting a chat.
6. Start a new chat, select this knowledge base, and ask about the researched
   topic. Open an answer's citations to compare the retrieved text with the
   answer.

RAG Web UI citations identify the uploaded document and its retrieved text.
The source URLs you included provide the route back to the original pages;
uploading Markdown does not create live links between the knowledge base and
those websites. Revisit the sources and upload revised notes when you need newer
information, then check retrieval again.
