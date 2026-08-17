"use client";

import { useEffect, useState } from "react";
import { ThumbsDown, ThumbsUp } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";
import { cn } from "@/lib/utils";

type FeedbackRating = "good" | "bad";

interface MessageFeedbackButtonsProps {
  chatId: string;
  messageId: string;
  initialRating?: FeedbackRating | null;
  disabled?: boolean;
}

export function MessageFeedbackButtons({
  chatId,
  messageId,
  initialRating = null,
  disabled = false,
}: MessageFeedbackButtonsProps) {
  const { toast } = useToast();
  const [rating, setRating] = useState<FeedbackRating | null>(initialRating);
  const [saving, setSaving] = useState(false);
  const isPersistedMessage = /^\d+$/.test(messageId);

  useEffect(() => {
    setRating(initialRating);
  }, [initialRating]);

  if (!isPersistedMessage) {
    return null;
  }

  const submitRating = async (nextRating: FeedbackRating) => {
    if (disabled || saving || !isPersistedMessage) {
      return;
    }

    setSaving(true);
    try {
      await api.post(`/api/chat/${chatId}/messages/${messageId}/feedback`, {
        rating: nextRating,
      });
      setRating(nextRating);
    } catch (error) {
      toast({
        title: "Could not save feedback",
        description:
          error instanceof ApiError ? error.message : "Please try again",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mt-2 flex items-center gap-1 text-muted-foreground">
      <button
        type="button"
        aria-label="Good response"
        disabled={disabled || saving}
        onClick={() => submitRating("good")}
        className={cn(
          "rounded-md p-1.5 transition-colors hover:bg-accent hover:text-foreground disabled:opacity-50",
          rating === "good" && "bg-emerald-50 text-emerald-600 hover:text-emerald-700"
        )}
      >
        <ThumbsUp className="h-4 w-4" />
      </button>
      <button
        type="button"
        aria-label="Bad response"
        disabled={disabled || saving}
        onClick={() => submitRating("bad")}
        className={cn(
          "rounded-md p-1.5 transition-colors hover:bg-accent hover:text-foreground disabled:opacity-50",
          rating === "bad" && "bg-red-50 text-red-600 hover:text-red-700"
        )}
      >
        <ThumbsDown className="h-4 w-4" />
      </button>
    </div>
  );
}
