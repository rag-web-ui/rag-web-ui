"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Bot, Trash2, Search } from "lucide-react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import { api, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";

interface Agent {
  id: number;
  name: string;
  created_at: string;
  description: string;
  level: string;
  position: string;
  model: string;
  projects: string[];
}

export default function AgentPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const { toast } = useToast();

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const data = await api.get("/api/agents");
      setAgents(data);
    } catch (error) {
      console.error("Failed to fetch agents:", error);
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
    if (!confirm("Are you sure you want to delete this agent?")) return;
    try {
      await api.delete(`/api/ai-agent/${id}`);
      setAgents((prev) => prev.filter((agent) => agent.id !== id));
      toast({
        title: "Success",
        description: "Agent deleted successfully",
      });
    } catch (error) {
      console.error("Failed to delete agent:", error);
      if (error instanceof ApiError) {
        toast({
          title: "Error",
          description: error.message,
          variant: "destructive",
        });
      }
    }
  };

  const filteredAgents = agents.filter((agent) =>
    agent.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="bg-card rounded-lg shadow-sm p-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                Your AI Agents
              </h2>
              <p className="text-muted-foreground mt-1">
                Manage and explore your AI agents
              </p>
            </div>
            <Link
              href="/dashboard/ai-agent/new"
              className="inline-flex items-center justify-center rounded-full bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors duration-200 shadow-sm hover:shadow-md"
            >
              <Plus className="mr-2 h-4 w-4" />
              Create New Agent
            </Link>
          </div>

          <div className="mt-6 relative">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search agents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-full border bg-background/50 focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all duration-200"
              />
            </div>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filteredAgents.map((agent) => (
            <div
              key={agent.id}
              className="group relative bg-card rounded-xl border shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden"
            >
              <Link href={`/dashboard/ai-agent/${agent.id}`}>
                <div className="p-5">
                  <div className="flex items-start gap-4">
                    <div className="bg-primary/10 rounded-lg p-2">
                      <Bot className="h-6 w-6 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-lg truncate group-hover:text-primary transition-colors">
                        {agent.name}
                      </h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        {agent.position} • Level: {agent.level} •{" "}
                        {new Date(agent.created_at).toLocaleDateString()}
                      </p>
                      <p className="text-sm text-muted-foreground mt-1">
                        Model: {agent.model}
                      </p>
                      <p className="text-sm text-muted-foreground mt-1">
                        Projects: {agent.projects?.join(", ") || "No projects"}
                      </p>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground mt-4 line-clamp-2">
                    {agent.description || "No description available"}
                  </p>
                </div>
              </Link>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  handleDelete(agent.id);
                }}
                className="absolute top-4 right-4 p-2 rounded-full hover:bg-destructive/10 group/delete"
              >
                <Trash2 className="h-4 w-4 text-muted-foreground group-hover/delete:text-destructive transition-colors" />
              </button>
            </div>
          ))}
        </div>

        {agents.length === 0 && (
          <div className="text-center py-16 bg-card rounded-lg border">
            <Bot className="mx-auto h-12 w-12 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-medium text-foreground">
              No AI agents yet
            </h3>
            <p className="mt-2 text-muted-foreground">
              Create a new AI agent to get started
            </p>
            <Link
              href="/dashboard/ai-agent/new"
              className="mt-6 inline-flex items-center justify-center rounded-full bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors duration-200"
            >
              <Plus className="mr-2 h-4 w-4" />
              Create Your First Agent
            </Link>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}