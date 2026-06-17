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
      const data = await api.get("/api/chat");
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
      await api.delete(`/api/chat/${id}`);
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
        <div className="bg-gradient-to-r from-slate-50 to-white rounded-xl shadow-sm p-6 border border-slate-200">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h2 className="text-4xl font-bold tracking-tight text-slate-900">
                Conversations
              </h2>
              <p className="text-slate-600 mt-2">
                Explore and manage your AI-powered conversations
              </p>
            </div>
            <Link
              href="/dashboard/chat/new"
              className="inline-flex items-center justify-center rounded-lg bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-all duration-200 shadow-md hover:shadow-lg"
            >
              <Plus className="mr-2 h-4 w-4" />
              Start New Chat
            </Link>
          </div>

          <div className="mt-6 relative">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
              <input
                type="text"
                placeholder="Search conversations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-900 placeholder-slate-500 focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all duration-200"
              />
            </div>
          </div>
        </div>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {filteredChats.map((chat) => (
            <div
              key={chat.id}
              className="group relative bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-lg transition-all duration-200 overflow-hidden hover:border-primary/30"
            >
              <Link href={`/dashboard/chat/${chat.id}`}>
                <div className="p-5">
                  <div className="flex items-start gap-4">
                    <div className="bg-primary/10 rounded-lg p-3">
                      <MessageSquare className="h-5 w-5 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-base truncate text-slate-900 group-hover:text-primary transition-colors">
                        {chat.title}
                      </h3>
                      <p className="text-xs text-slate-500 mt-1.5">
                        {chat.messages.length} messages • {new Date(chat.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  {chat.messages.length > 0 && (
                    <p className="text-sm text-slate-600 mt-4 line-clamp-2">
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
                className="absolute top-4 right-4 p-2 rounded-lg hover:bg-red-50 group/delete transition-colors"
              >
                <Trash2 className="h-4 w-4 text-slate-400 group-hover/delete:text-red-600 transition-colors" />
              </button>
            </div>
          ))}
        </div>

        {chats.length === 0 && (
          <div className="text-center py-16 bg-slate-50 rounded-xl border border-dashed border-slate-300">
            <MessageSquare className="mx-auto h-12 w-12 text-slate-400" />
            <h3 className="mt-4 text-lg font-semibold text-slate-900">
              No conversations yet
            </h3>
            <p className="mt-2 text-slate-600">
              Start a new chat to begin exploring your knowledge base
            </p>
            <Link
              href="/dashboard/chat/new"
              className="mt-6 inline-flex items-center justify-center rounded-lg bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-all duration-200 shadow-md hover:shadow-lg"
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
