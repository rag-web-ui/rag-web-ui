import React, {
  FC,
  useMemo,
  useEffect,
  useState,
  ClassAttributes,
} from "react";
import { AnchorHTMLAttributes } from "react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Skeleton } from "@/components/ui/skeleton";
import Markdown from "react-markdown";

interface Citation {
  id: number;
  text: string;
  metadata: Record<string, any>;
}

export const Answer: FC<{
  markdown: string;
  citations?: Citation[];
}> = ({ markdown, citations = [] }) => {
  console.log("citations", citations);
  const CitationLink = useMemo(
    () =>
      (
        props: ClassAttributes<HTMLAnchorElement> &
          AnchorHTMLAttributes<HTMLAnchorElement>
      ) => {
        const citationId = props.href?.match(/^(\d+)$/)?.[1];
        const citation = citationId
          ? citations[parseInt(citationId) - 1]
          : null;

        if (!citation) {
          return <a {...props}>[{props.href}]</a>;
        }

        console.log("citation", citation);
        console.log("citations 1", citations[0]);
        console.log("citations 2", citations[1]);
        console.log("citations 3", citations[2]);

        return (
          <Popover>
            <PopoverTrigger asChild>
              <a
                {...props}
                href="#"
                role="button"
                className="text-blue-600 underline cursor-pointer"
              >
                [{props.href}]
              </a>
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
    [citations]
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

  return (
    <div className="prose prose-sm max-w-full">
      <Markdown
        components={{
          a: CitationLink,
        }}
      >
        {markdown}
      </Markdown>
    </div>
  );
};
