import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Skeleton } from "@/components/ui/skeleton";
import { FC, useMemo, useEffect, useState } from "react";
import Markdown from "react-markdown";

const markdownParse = (text: string) => {
  return text
    .replace(/\[\[([cC])itation/g, "[citation")
    .replace(/[cC]itation:(\d+)]]/g, "citation:$1]")
    .replace(/\[\[([cC]itation:\d+)]](?!])/g, `[$1]`)
    .replace(/\[[cC]itation:(\d+)]/g, "[citation]($1)");
};

interface Citation {
  id: number;
  text: string;
  metadata: Record<string, any>;
}

interface ParsedResponse {
  citations: Citation[];
  text: string;
}

export const Answer: FC<{ markdown: string }> = ({ markdown }) => {
  const [parsedContent, setParsedContent] = useState<{
    citations: Citation[];
    text: string;
    parsed: string;
  }>({ citations: [], text: "", parsed: "" });

  const parseResponse = useMemo(
    () =>
      (markdown: string): ParsedResponse => {
        if (!markdown) return { citations: [], text: "" };

        if (!markdown.includes("__LLM_RESPONSE__")) {
          return { citations: [], text: markdown };
        }

        const [base64Part, responseText] = markdown.split("__LLM_RESPONSE__");

        try {
          const contextData = base64Part
            ? (JSON.parse(atob(base64Part)) as {
                context: Array<{
                  page_content: string;
                  metadata: Record<string, any>;
                }>;
              })
            : null;

          const citations: Citation[] =
            contextData?.context.map((citation, index) => ({
              id: index + 1,
              text: citation.page_content,
              metadata: citation.metadata,
            })) || [];

          return {
            citations,
            text: responseText || "",
          };
        } catch (e) {
          console.error("Failed to parse response:", e);
          return { citations: [], text: "" };
        }
      },
    []
  );

  useEffect(() => {
    if (!markdown) return;

    const { citations, text } = parseResponse(markdown);
    const parsed = text ? markdownParse(text) : "";

    setParsedContent({ citations, text, parsed });
  }, [markdown, parseResponse]);

  const CitationLink = useMemo(
    () =>
      ({ href }: { href: string }) => {
        const citationId = href.match(/^(\d+)$/)?.[1];
        const citation = citationId
          ? parsedContent.citations[parseInt(citationId) - 1]
          : null;

        if (!citation) {
          return (
            <span className="text-blue-600 underline" data-citation-link>
              [{href}]
            </span>
          );
        }

        return (
          <Popover>
            <PopoverTrigger asChild>
              <span
                role="button"
                className="text-blue-600 underline cursor-pointer"
              >
                [{href}]
              </span>
            </PopoverTrigger>
            <PopoverContent
              side="top"
              align="start"
              className="max-w-2xl w-[calc(100vw-100px)]"
            >
              <div className="text-sm">
                <p className="text-gray-700">{citation.text}</p>
                {Object.keys(citation.metadata).length > 0 && (
                  <div className="mt-2 text-xs text-gray-500">
                    {Object.entries(citation.metadata).map(([key, value]) => (
                      <div key={key}>
                        <span className="font-medium">{key}: </span>
                        {String(value)}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </PopoverContent>
          </Popover>
        );
      },
    [parsedContent.citations]
  );

  if (!markdown) {
    return (
      <div className="flex flex-col gap-2">
        <Skeleton className="max-w-sm h-4 bg-zinc-200" />
        <Skeleton className="max-w-lg h-4 bg-zinc-200" />
        <Skeleton className="max-w-2xl h-4 bg-zinc-200" />
        <Skeleton className="max-w-lg h-4 bg-zinc-200" />
        <Skeleton className="max-w-xl h-4 bg-zinc-200" />
      </div>
    );
  }

  if (!parsedContent.text) {
    return null;
  }

  return (
    <div className="prose prose-sm max-w-full">
      <Markdown
        components={{
          a: CitationLink,
        }}
      >
        {parsedContent.parsed}
      </Markdown>
    </div>
  );
};
