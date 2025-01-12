"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, MessageSquare, Trash2 } from "lucide-react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import { api, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";

interface Chat {
  id: number;
  title: string;
  created_at: string;
  messages: Message[];
  knowledge_base_ids: number[];
}

interface Message {
  id: number;
  content: string;
  is_bot: boolean;
  created_at: string;
}

export default function ChatPage() {
  const [chats, setChats] = useState<Chat[]>([]);
  const { toast } = useToast();

  useEffect(() => {
    fetchChats();
  }, []);

  const fetchChats = async () => {
    try {
      const data = await api.get<Chat[]>("http://localhost:8000/api/chat");
      setChats(data);
    } catch (error) {
      console.error("Failed to fetch chats:", error);
      if (error instanceof ApiError) {
        toast({
          title: "Error",
          description: error.message,
          variant: "destructive",
        });
      }
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this chat?")) return;

    try {
      await api.delete<void>(`http://localhost:8000/api/chat/${id}`);
      setChats((prev) => prev.filter((chat) => chat.id !== id));
      toast({
        title: "Success",
        description: "Chat deleted successfully",
      });
    } catch (error) {
      console.error("Failed to delete chat:", error);
      if (error instanceof ApiError) {
        toast({
          title: "Error",
          description: error.message,
          variant: "destructive",
        });
      }
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Chats</h2>
            <p className="text-muted-foreground">
              Your conversations with the knowledge base
            </p>
          </div>
          <Link
            href="/dashboard/chat/new"
            className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            <Plus className="mr-2 h-4 w-4" />
            New Chat
          </Link>
        </div>

        <div className="grid gap-6">
          {chats.map((chat) => (
            <div key={chat.id} className="rounded-lg border bg-card p-6">
              <div className="flex justify-between items-start">
                <Link
                  href={`/dashboard/chat/${chat.id}`}
                  className="flex items-start space-x-4 flex-1"
                >
                  <MessageSquare className="h-8 w-8 text-primary mt-1" />
                  <div>
                    <h3 className="font-semibold hover:underline">
                      {chat.title}
                    </h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      {chat.messages.length} messages •{" "}
                      {new Date(chat.created_at).toLocaleDateString()}
                    </p>
                    {chat.messages.length > 0 && (
                      <p className="text-sm text-muted-foreground mt-2 line-clamp-2">
                        {chat.messages[chat.messages.length - 1].content}
                      </p>
                    )}
                  </div>
                </Link>
                <button
                  onClick={() => handleDelete(chat.id)}
                  className="p-2 hover:bg-accent rounded-md"
                >
                  <Trash2 className="h-4 w-4 text-muted-foreground" />
                </button>
              </div>
            </div>
          ))}

          {chats.length === 0 && (
            <div className="text-center py-12">
              <p className="text-muted-foreground">
                No chats found. Start a new conversation to get started.
              </p>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
