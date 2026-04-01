"use client";

import { useEffect, useRef, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useChat } from "ai/react";
import { Send, User, ThumbsDown, ThumbsUp } from "lucide-react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import { api, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";
import { Answer } from "@/components/chat/answer";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface Message {
  id: string;
  role: "assistant" | "user" | "system" | "data";
  content: string;
  citations?: Citation[];
  feedbackType?: "up" | "down" | null;
  feedbackNote?: string | null;
  correctedAnswer?: string | null;
  feedbackQuery?: string | null;
}

interface ChatMessage {
  id: number;
  content: string;
  role: "assistant" | "user";
  created_at: string;
  feedback_type?: "up" | "down" | null;
  feedback_note?: string | null;
  corrected_answer?: string | null;
  feedback_query?: string | null;
}

interface Chat {
  id: number;
  title: string;
  messages: ChatMessage[];
}

interface Citation {
  id: number;
  text: string;
  metadata: Record<string, any>;
}

// Extend the default useChat message type
declare module "ai/react" {
  interface Message {
    citations?: Citation[];
    feedbackType?: "up" | "down" | null;
    feedbackNote?: string | null;
    correctedAnswer?: string | null;
    feedbackQuery?: string | null;
  }
}

export default function ChatPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [feedbackDialogOpen, setFeedbackDialogOpen] = useState(false);
  const [selectedFeedbackMessage, setSelectedFeedbackMessage] =
    useState<Message | null>(null);
  const [feedbackDescription, setFeedbackDescription] = useState("");
  const [correctedAnswer, setCorrectedAnswer] = useState("");
  const prevLoadingRef = useRef(false);

  const {
    messages,
    data,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    setMessages,
  } = useChat({
    api: `/api/chat/${params.id}/messages`,
    headers: {
      Authorization: `Bearer ${
        typeof window !== "undefined"
          ? window.localStorage.getItem("token")
          : ""
      }`,
    },
  });

  useEffect(() => {
    if (isInitialLoad) {
      fetchChat();
      setIsInitialLoad(false);
    }
  }, [isInitialLoad]);

  useEffect(() => {
    if (!isInitialLoad) {
      scrollToBottom();
    }
  }, [messages, isInitialLoad]);

  const fetchChat = async () => {
    try {
      const data: Chat = await api.get(`/api/chat/${params.id}`);
      const formattedMessages = data.messages.map((msg) => {
        if (msg.role !== "assistant" || !msg.content)
          return {
            id: msg.id.toString(),
            role: msg.role,
            content: msg.content,
            feedbackType: msg.feedback_type ?? null,
            feedbackNote: msg.feedback_note ?? null,
            correctedAnswer: msg.corrected_answer ?? null,
            feedbackQuery: msg.feedback_query ?? null,
          };

        try {
          if (!msg.content.includes("__LLM_RESPONSE__")) {
            return {
              id: msg.id.toString(),
              role: msg.role,
              content: msg.content,
            };
          }

          const [base64Part, responseText] =
            msg.content.split("__LLM_RESPONSE__");

          const contextData = base64Part
            ? (JSON.parse(atob(base64Part.trim())) as {
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
            id: msg.id.toString(),
            role: msg.role,
            content: responseText || "",
            citations,
            feedbackType: msg.feedback_type ?? null,
            feedbackNote: msg.feedback_note ?? null,
            correctedAnswer: msg.corrected_answer ?? null,
            feedbackQuery: msg.feedback_query ?? null,
          };
        } catch (e) {
          console.error("Failed to process message:", e);
          return {
            id: msg.id.toString(),
            role: msg.role,
            content: msg.content,
            feedbackType: msg.feedback_type ?? null,
            feedbackNote: msg.feedback_note ?? null,
            correctedAnswer: msg.corrected_answer ?? null,
            feedbackQuery: msg.feedback_query ?? null,
          };
        }
      });
      setMessages(formattedMessages);
    } catch (error) {
      console.error("Failed to fetch chat:", error);
      if (error instanceof ApiError) {
        toast({
          title: "Error",
          description: error.message,
          variant: "destructive",
        });
      }
      router.push("/dashboard/chat");
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const processMessageContent = (message: Message): Message => {
    if (message.role !== "assistant" || !message.content) return message;

    try {
      if (!message.content.includes("__LLM_RESPONSE__")) {
        return message;
      }

      const [base64Part, responseText] =
        message.content.split("__LLM_RESPONSE__");

      const contextData = base64Part
        ? (JSON.parse(atob(base64Part.trim())) as {
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
        ...message,
        content: responseText || "",
        citations,
      };
    } catch (e) {
      console.error("Failed to process message:", e);
      return message;
    }
  };

  const markdownParse = (text: string) => {
    return text
      .replace(/\[\[([cC])itation/g, "[citation")
      .replace(/[cC]itation:(\d+)]]/g, "citation:$1]")
      .replace(/\[\[([cC]itation:\d+)]](?!])/g, `[$1]`)
      .replace(/\[[cC]itation:(\d+)]/g, "[citation]($1)");
  };

  const processedMessages = useMemo(() => {
    return messages.map((message) => {
      if (message.role !== "assistant" || !message.content) return message;

      try {
        if (!message.content.includes("__LLM_RESPONSE__")) {
          return {
            ...message,
            content: markdownParse(message.content),
          };
        }

        const [base64Part, responseText] =
          message.content.split("__LLM_RESPONSE__");

        const contextData = base64Part
          ? (JSON.parse(atob(base64Part.trim())) as {
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
          ...message,
          content: markdownParse(responseText || ""),
          citations,
        };
      } catch (e) {
        console.error("Failed to process message:", e);
        return message;
      }
    });
  }, [messages]);

  // Step 1: Check if feedback is required
  const lastAssistantMessage = processedMessages
    .slice()
    .reverse()
    .find((msg) => msg.role === "assistant");

  const isFeedbackRequired = lastAssistantMessage
    ? !lastAssistantMessage.feedbackType
    : false;

  useEffect(() => {
    if (!prevLoadingRef.current && isLoading) {
      prevLoadingRef.current = true;
      return;
    }
    if (prevLoadingRef.current && !isLoading) {
      prevLoadingRef.current = false;
      fetchChat();
    }
  }, [isLoading]);

  const getPreviousUserQuestion = (messageId: string): string => {
    const messageIndex = processedMessages.findIndex((msg) => msg.id === messageId);
    if (messageIndex <= 0) {
      return "";
    }

    for (let i = messageIndex - 1; i >= 0; i -= 1) {
      if (processedMessages[i].role === "user") {
        return processedMessages[i].content;
      }
    }

    return "";
  };

  const canSubmitFeedback = (message: Message): boolean => !Number.isNaN(Number(message.id));

  const handleThumbsUp = async (message: Message) => {
    if (!canSubmitFeedback(message)) {
      toast({
        title: "Please wait",
        description: "Feedback will be available after message is saved.",
      });
      return;
    }

    const userQuery = getPreviousUserQuestion(message.id);
    try {
      await api.post(`/api/chat/${params.id}/messages/${message.id}/feedback`, {
        feedback_type: "up",
        user_query: userQuery,
        assistant_response: message.content,
      });
      toast({
        title: "Thanks for the feedback",
        description: "This answer will be preferred for the same question.",
      });
      fetchChat();
    } catch (error) {
      toast({
        title: "Feedback failed",
        description:
          error instanceof ApiError ? error.message : "Something went wrong",
        variant: "destructive",
      });
    }
  };

  const openThumbsDownDialog = (message: Message) => {
    if (!canSubmitFeedback(message)) {
      toast({
        title: "Please wait",
        description: "Feedback will be available after message is saved.",
      });
      return;
    }
    setSelectedFeedbackMessage(message);
    setFeedbackDescription(message.feedbackNote || "");
    setCorrectedAnswer(message.correctedAnswer || "");
    setFeedbackDialogOpen(true);
  };

  const submitThumbsDown = async () => {
    if (!selectedFeedbackMessage) {
      return;
    }
    const userQuery = getPreviousUserQuestion(selectedFeedbackMessage.id);
    try {
      await api.post(
        `/api/chat/${params.id}/messages/${selectedFeedbackMessage.id}/feedback`,
        {
          feedback_type: "down",
          user_query: userQuery,
          assistant_response: selectedFeedbackMessage.content,
          corrected_answer: correctedAnswer,
          feedback_note: feedbackDescription,
        }
      );
      setFeedbackDialogOpen(false);
      setSelectedFeedbackMessage(null);
      setFeedbackDescription("");
      setCorrectedAnswer("");
      toast({
        title: "Feedback saved",
        description: "Your correction will be preferred for this question next time.",
      });
      fetchChat();
    } catch (error) {
      toast({
        title: "Feedback failed",
        description:
          error instanceof ApiError ? error.message : "Something went wrong",
        variant: "destructive",
      });
    }
  };

  return (
    <DashboardLayout>
      <div className="flex flex-col h-[calc(100vh-5rem)] relative">
        <div className="flex-1 overflow-y-auto p-4 space-y-4 pb-[80px]">
          {processedMessages.map((message) =>
            message.role === "assistant" ? (
              <div
                key={message.id}
                className="flex justify-start items-start space-x-2"
              >
                <div className="w-8 h-8 flex items-center justify-center">
                  <img
                    src="/logo.png"
                    className="h-8 w-8 rounded-full"
                    alt="logo"
                  />
                </div>
                <div className="max-w-[80%] rounded-lg px-4 py-2 text-accent-foreground">
                  <Answer
                    key={message.id}
                    markdown={message.content}
                    citations={message.citations}
                  />
                  <div className="mt-3 flex items-center gap-2">
                    <Button
                      type="button"
                      variant={message.feedbackType === "up" ? "default" : "outline"}
                      size="sm"
                      onClick={() => handleThumbsUp(message)}
                    >
                      <ThumbsUp className="h-4 w-4" />
                    </Button>
                    <Button
                      type="button"
                      variant={message.feedbackType === "down" ? "default" : "outline"}
                      size="sm"
                      onClick={() => openThumbsDownDialog(message)}
                    >
                      <ThumbsDown className="h-4 w-4" />
                    </Button>
                    {message.feedbackType && (
                      <span className="text-xs text-muted-foreground">
                        Feedback saved ({message.feedbackType === "up" ? "helpful" : "needs correction"})
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div
                key={message.id}
                className="flex justify-end items-start space-x-2"
              >
                <div className="max-w-[80%] rounded-lg px-4 py-2 bg-primary text-primary-foreground">
                  {message.content}
                </div>
                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                  <User className="h-5 w-5 text-primary-foreground" />
                </div>
              </div>
            )
          )}
          <div className="flex justify-start">
            {isLoading &&
              processedMessages[processedMessages.length - 1]?.role !=
                "assistant" && (
                <div className="max-w-[80%] rounded-lg px-4 py-2 text-accent-foreground">
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 rounded-full bg-primary animate-bounce" />
                    <div className="w-2 h-2 rounded-full bg-primary animate-bounce [animation-delay:0.2s]" />
                    <div className="w-2 h-2 rounded-full bg-primary animate-bounce [animation-delay:0.4s]" />
                  </div>
                </div>
              )}
          </div>
          <div ref={messagesEndRef} />
        </div>
        <form
          onSubmit={handleSubmit}
          className="border-t p-4 flex items-center space-x-4 bg-background absolute bottom-0 left-0 right-0"
        >
          <input
            value={input}
            onChange={handleInputChange}
            placeholder={
              isFeedbackRequired
                ? "Please provide feedback on the last answer first..."
                : "Type your message..."
            }
            disabled={isFeedbackRequired || isLoading}
            className="flex-1 min-w-0 h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim() || isFeedbackRequired}
            className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
      <Dialog open={feedbackDialogOpen} onOpenChange={setFeedbackDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Improve this answer</DialogTitle>
            <DialogDescription>
              Share the correct answer or a description. This will be used first for the same question next time.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Correct answer</label>
              <textarea
                value={correctedAnswer}
                onChange={(e) => setCorrectedAnswer(e.target.value)}
                rows={4}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="Enter the corrected answer"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Description</label>
              <textarea
                value={feedbackDescription}
                onChange={(e) => setFeedbackDescription(e.target.value)}
                rows={3}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="Describe what was wrong (optional if answer provided)"
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setFeedbackDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              type="button"
              onClick={submitThumbsDown}
              disabled={!correctedAnswer.trim() && !feedbackDescription.trim()}
            >
              Save feedback
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
