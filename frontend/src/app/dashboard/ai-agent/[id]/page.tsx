"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import DashboardLayout from "@/components/layout/dashboard-layout";
import { api, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";

interface Agent {
  id: number;
  name: string;
  level: string;
  position: string;
  model: string;
  projects: string[] | null;
  status: "on" | "off";
  server: string | null;
  usage_time: string | null;
  created_at: string;
}

interface Task {
  id: number;
  description: string;
  status: string;
  completed_at: string | null;
}

export default function AgentDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const { toast } = useToast();
  const [agent, setAgent] = useState<Agent | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      await Promise.all([fetchAgent(), fetchTasks()]);
    };
    fetchData();
  }, []);

  const fetchAgent = async () => {
    try {
      const response = await api.get(`/api/agents/${params.id}`);
      setAgent(response as Agent);
      setIsLoading(false);
    } catch (error) {
      console.error("Failed to fetch agent:", error);
      if (error instanceof ApiError) {
        setError(error.message);
        toast({
          title: "Error",
          description: error.message,
          variant: "destructive",
        });
      } else {
        setError("Failed to fetch agent");
      }
      router.push("/dashboard/agents");
    }
  };

  const fetchTasks = async () => {
    try {
      const response = await api.get(`/api/agents/${params.id}/tasks`);
      setTasks(response as Task[]);
    } catch (error) {
      console.error("Failed to fetch tasks:", error);
      if (error instanceof ApiError) {
        toast({
          title: "Error",
          description: error.message,
          variant: "destructive",
        });
      }
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (error || !agent) {
    return (
      <DashboardLayout>
        <div className="max-w-2xl mx-auto text-center py-16">
          <h2 className="text-3xl font-bold tracking-tight mb-4">Agent Not Found</h2>
          <p className="text-muted-foreground mb-8">{error || "The requested agent could not be found."}</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-8 p-6">
        {/* Agent Information */}
        <div className="bg-card rounded-lg shadow-sm p-6">
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            {agent.name}
          </h2>
          <p className="text-muted-foreground mt-1">Agent Details</p>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Level</p>
              <p className="text-lg">{agent.level || "N/A"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Position</p>
              <p className="text-lg">{agent.position === "dev" ? "Developer" : "Tester"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Model</p>
              <p className="text-lg">{agent.model || "N/A"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Projects</p>
              <p className="text-lg">{agent.projects?.join(", ") || "No projects"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Status</p>
              <p className="text-lg">
                <span
                  className={`inline-block w-3 h-3 rounded-full mr-2 ${
                    agent.status === "on" ? "bg-green-500" : "bg-red-500"
                  }`}
                ></span>
                {agent.status === "on" ? "Online" : "Offline"}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Server</p>
              <p className="text-lg">{agent.server || "N/A"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Usage Time</p>
              <p className="text-lg">{agent.usage_time || "N/A"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Created At</p>
              <p className="text-lg">{new Date(agent.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        </div>

        {/* Tasks Section */}
        <div className="bg-card rounded-lg shadow-sm p-6">
          <h3 className="text-2xl font-bold tracking-tight">Tasks Completed</h3>
          <p className="text-muted-foreground mt-1">List of tasks performed by this agent</p>
          <div className="mt-4 space-y-4">
            {tasks.length === 0 ? (
              <p className="text-muted-foreground">No tasks completed yet.</p>
            ) : (
              tasks.map((task) => (
                <div
                  key={task.id}
                  className="border rounded-lg p-4 hover:bg-accent transition-colors"
                >
                  <p className="font-medium">{task.description}</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Status: {task.status} • Completed: {task.completed_at ? new Date(task.completed_at).toLocaleDateString() : "N/A"}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}