"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, MessageSquare, Trash2, Search } from "lucide-react";
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
  const [searchTerm, setSearchTerm] = useState("");
  const { toast } = useToast();

  useEffect(() => {
    fetchChats();
  }, []);

  const fetchChats = async () => {
    try {
      const data = await api.get("http://localhost:8000/api/chat");
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
      await api.delete(`http://localhost:8000/api/chat/${id}`);
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

  const filteredChats = chats.filter((chat) =>
    chat.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="bg-card rounded-lg shadow-sm p-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                Your Conversations
              </h2>
              <p className="text-muted-foreground mt-1">
                Explore and manage your chat history
              </p>
            </div>
            <Link
              href="/dashboard/chat/new"
              className="inline-flex items-center justify-center rounded-full bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors duration-200 shadow-sm hover:shadow-md"
            >
              <Plus className="mr-2 h-4 w-4" />
              Start New Chat
            </Link>
          </div>

          <div className="mt-6 relative">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search conversations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-full border bg-background/50 focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all duration-200"
              />
            </div>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filteredChats.map((chat) => (
            <div
              key={chat.id}
              className="group relative bg-card rounded-xl border shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden"
            >
              <Link href={`/dashboard/chat/${chat.id}`}>
                <div className="p-5">
                  <div className="flex items-start gap-4">
                    <div className="bg-primary/10 rounded-lg p-2">
                      <MessageSquare className="h-6 w-6 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-lg truncate group-hover:text-primary transition-colors">
                        {chat.title}
                      </h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        {chat.messages.length} messages •{" "}
                        {new Date(chat.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  {chat.messages.length > 0 && (
                    <p className="text-sm text-muted-foreground mt-4 line-clamp-2">
                      {chat.messages[chat.messages.length - 1].content.includes(
                        "__LLM_RESPONSE__"
                      )
                        ? chat.messages[chat.messages.length - 1].content.split(
                            "__LLM_RESPONSE__"
                          )[1]
                        : chat.messages[chat.messages.length - 1].content}
                    </p>
                  )}
                </div>
              </Link>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  handleDelete(chat.id);
                }}
                className="absolute top-4 right-4 p-2 rounded-full hover:bg-destructive/10 group/delete"
              >
                <Trash2 className="h-4 w-4 text-muted-foreground group-hover/delete:text-destructive transition-colors" />
              </button>
            </div>
          ))}
        </div>

        {chats.length === 0 && (
          <div className="text-center py-16 bg-card rounded-lg border">
            <MessageSquare className="mx-auto h-12 w-12 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-medium text-foreground">
              No conversations yet
            </h3>
            <p className="mt-2 text-muted-foreground">
              Start a new chat to begin exploring your knowledge base
            </p>
            <Link
              href="/dashboard/chat/new"
              className="mt-6 inline-flex items-center justify-center rounded-full bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors duration-200"
            >
              <Plus className="mr-2 h-4 w-4" />
              Start Your First Chat
            </Link>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
