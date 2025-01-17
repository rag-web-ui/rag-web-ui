import React from "react";
import { cn } from "@/lib/utils";

interface DividerProps {
  className?: string;
  orientation?: "horizontal" | "vertical";
}

export const Divider: React.FC<DividerProps> = ({
  className,
  orientation = "horizontal",
}) => {
  return (
    <div
      className={cn(
        "bg-gray-200",
        "my-1",
        orientation === "horizontal"
          ? "h-[1px] w-full"
          : "w-[1px] h-full min-h-[20px]",
        className
      )}
      role="separator"
    />
  );
};
