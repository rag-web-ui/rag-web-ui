"use client";

import { useParams } from "next/navigation";
import { useState, useCallback } from "react";
import { DocumentUploadSteps } from "@/components/knowledge-base/document-upload-steps";
import { DocumentVideoUploadSteps } from "@/components/knowledge-base/document-video-upload-steps";
import { DocumentImageUploadSteps } from "@/components/knowledge-base/document-image-upload-steps";
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
import { PlusIcon } from "lucide-react";
import DashboardLayout from "@/components/layout/dashboard-layout";

export default function KnowledgeBasePage() {
  const params = useParams();
  const knowledgeBaseId = parseInt(params.id as string);
  const [refreshKey, setRefreshKey] = useState(0);
  const [dialogOpen, setDialogOpen] = useState(false);

  const handleUploadComplete = useCallback(() => {
    setRefreshKey((prev) => prev + 1);
    setDialogOpen(false);
  }, []);

  return (
    <DashboardLayout>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Knowledge Base</h1>
        <div className="flex justify-between items-center gap-2">
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
          <Dialog>
            <DialogTrigger asChild>
              <Button>
                <PlusIcon className="w-4 h-4 mr-2" />
                Add Video
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl">
              <DialogHeader>
                <DialogTitle>Add Video</DialogTitle>
                <DialogDescription>
                  Upload your video link here (e.g., YouTube, Vimeo, etc.) to add it to your knowledge base.
                </DialogDescription>
              </DialogHeader>
              <DocumentVideoUploadSteps
                knowledgeBaseId={knowledgeBaseId}
                onComplete={handleUploadComplete}
              />
            </DialogContent>
          </Dialog>
          <Dialog>
            <DialogTrigger asChild>
              <Button>
                <PlusIcon className="w-4 h-4 mr-2" />
                Add Image
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl">
              <DialogHeader>
                <DialogTitle>Add Image</DialogTitle>
                <DialogDescription>
                  Upload an image to your knowledge base. Supported formats: PNG, JPG, JPEG, GIF, and other common image files.
                </DialogDescription>
              </DialogHeader>
              <DocumentImageUploadSteps
                knowledgeBaseId={knowledgeBaseId}
                onComplete={handleUploadComplete}
              />
            </DialogContent>
          </Dialog>
          <Dialog>
            <DialogTrigger asChild>
              <Button>
                <PlusIcon className="w-4 h-4 mr-2" />
                Add Source Code
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl">
              <DialogHeader>
                <DialogTitle>Add Source Code</DialogTitle>
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
        </div>
      </div>

      <div className="mt-8">
        <DocumentList key={refreshKey} knowledgeBaseId={knowledgeBaseId} />
      </div>
    </DashboardLayout>
  );
}
