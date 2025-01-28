"use client";

import { useParams } from "next/navigation";
import { useState, useCallback, useEffect } from "react";
import { DocumentUploadSteps } from "@/components/knowledge-base/document-upload-steps";
import { DocumentList } from "@/components/knowledge-base/document-list";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { PlusIcon, Settings } from "lucide-react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import { api, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";

interface KnowledgeBase {
  id: number;
  name: string;
  description: string;
  embeddings_service: string;
  documents: any[];
}

export default function KnowledgeBasePage() {
  const params = useParams();
  const knowledgeBaseId = parseInt(params.id as string);
  const [refreshKey, setRefreshKey] = useState(0);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [settingsDialogOpen, setSettingsDialogOpen] = useState(false);
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBase | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();

  const fetchKnowledgeBase = async () => {
    try {
      const data = await api.get(`/api/knowledge-base/${knowledgeBaseId}`);
      setKnowledgeBase(data);
    } catch (error) {
      console.error("Failed to fetch knowledge base:", error);
      if (error instanceof ApiError) {
        toast({
          title: "Error",
          description: error.message,
          variant: "destructive",
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchKnowledgeBase();
  }, [knowledgeBaseId]);

  const handleUploadComplete = useCallback(() => {
    setRefreshKey((prev) => prev + 1);
    setDialogOpen(false);
  }, []);

  const handleSettingsSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const formData = new FormData(e.currentTarget);
      const embeddings_service = formData.get("embeddings_service") as string;

      await api.put(`/api/knowledge-base/${knowledgeBaseId}`, {
        embeddings_service,
      });

      await fetchKnowledgeBase();
      setSettingsDialogOpen(false);
      toast({
        title: "Success",
        description: "Knowledge base settings updated successfully",
      });
    } catch (error) {
      console.error("Failed to update knowledge base:", error);
      if (error instanceof ApiError) {
        toast({
          title: "Error",
          description: error.message,
          variant: "destructive",
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading || !knowledgeBase) {
    return (
      <DashboardLayout>
        <div className="flex justify-center items-center min-h-[200px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">{knowledgeBase.name}</h1>
            <p className="text-muted-foreground mt-1">
              {knowledgeBase.description || "No description"}
            </p>
            <div className="flex items-center gap-2 mt-2">
              <span className="inline-flex items-center rounded-full px-2 py-1 text-xs font-medium bg-primary/10 text-primary">
                {knowledgeBase.embeddings_service === "openai" ? "OpenAI" : "Ollama"}
              </span>
              <button
                onClick={() => setSettingsDialogOpen(true)}
                className="inline-flex items-center text-xs text-muted-foreground hover:text-primary"
              >
                <Settings className="w-3 h-3 mr-1" />
                Settings
              </button>
            </div>
          </div>

          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <PlusIcon className="w-4 h-4 mr-2" />
                Add Document
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl">
              <DialogHeader>
                <DialogTitle>Add Document</DialogTitle>
                <DialogDescription>
                  Upload a document to your knowledge base. Supported formats:
                  PDF, DOCX, Markdown, and Text files.
                </DialogDescription>
              </DialogHeader>
              <DocumentUploadSteps
                knowledgeBaseId={knowledgeBaseId}
                onComplete={handleUploadComplete}
              />
            </DialogContent>
          </Dialog>

          <Dialog open={settingsDialogOpen} onOpenChange={setSettingsDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Knowledge Base Settings</DialogTitle>
                <DialogDescription>
                  Update your knowledge base settings
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSettingsSubmit} className="space-y-4">
                <div className="space-y-2">
                  <label
                    htmlFor="embeddings_service"
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                  >
                    Embeddings Service
                  </label>
                  <select
                    id="embeddings_service"
                    name="embeddings_service"
                    defaultValue={knowledgeBase.embeddings_service}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <option value="openai">OpenAI</option>
                    <option value="ollama">Ollama</option>
                  </select>
                  <p className="text-sm text-muted-foreground mt-1">
                  Select the service for embedding documents. OpenAI provides better quality but requires an API key, while Ollama can run locally but the quality may be lower.
                  </p>
                </div>

                <div className="flex justify-end space-x-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setSettingsDialogOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? "Saving..." : "Save"}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        <div className="mt-8">
          <DocumentList key={refreshKey} knowledgeBaseId={knowledgeBaseId} />
        </div>
      </div>
    </DashboardLayout>
  );
}
