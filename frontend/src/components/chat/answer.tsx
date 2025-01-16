import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Skeleton } from "@/components/ui/skeleton";
import { FC } from "react";
import Markdown from "react-markdown";

const markdownParse = (text: string) => {
  return text
    .replace(/\[\[([cC])itation/g, "[citation")
    .replace(/[cC]itation:(\d+)]]/g, "citation:$1]")
    .replace(/\[\[([cC]itation:\d+)]](?!])/g, `[$1]`)
    .replace(/\[[cC]itation:(\d+)]/g, "[citation]($1)");
};

export const Answer: FC<{ markdown: string }> = ({ markdown }) => {
  const parsed = markdown ? markdownParse(markdown) : "";
  return (
    <>
      {markdown ? (
        <div className="prose prose-sm max-w-full">
          <Markdown
            components={{
              a: ({ node, ...props }) => {
                const href = props.href as string;
                return (
                  <a className="text-blue-600 underline" {...props}>
                    [{href}]
                  </a>
                );
              },
            }}
          >
            {parsed}
          </Markdown>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          <Skeleton className="max-w-sm h-4 bg-zinc-200" />
          <Skeleton className="max-w-lg h-4 bg-zinc-200" />
          <Skeleton className="max-w-2xl h-4 bg-zinc-200" />
          <Skeleton className="max-w-lg h-4 bg-zinc-200" />
          <Skeleton className="max-w-xl h-4 bg-zinc-200" />
        </div>
      )}
    </>
  );
};
