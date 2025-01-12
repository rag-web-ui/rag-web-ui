"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { formatDistanceToNow } from "date-fns";
import { api, ApiError } from "@/lib/api";

interface Document {
  id: number;
  title: string;
  file_path: string;
  file_size: number;
  content_type: string;
  created_at: string;
  processing_tasks: Array<{
    id: number;
    status: string;
    error_message: string | null;
  }>;
}

interface KnowledgeBase {
  id: number;
  name: string;
  description: string;
  documents: Document[];
}

interface DocumentListProps {
  knowledgeBaseId: number;
}

export function DocumentList({ knowledgeBaseId }: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const data = await api.get<KnowledgeBase>(
          `http://localhost:8000/api/knowledge-base/${knowledgeBaseId}`
        );
        setDocuments(data.documents);
      } catch (error) {
        if (error instanceof ApiError) {
          setError(error.message);
        } else {
          setError("Failed to fetch documents");
        }
      }
    };

    fetchDocuments();
  }, [knowledgeBaseId]);

  if (error) {
    return (
      <div className="flex justify-center items-center p-8">
        <p className="text-destructive">{error}</p>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="flex justify-center items-center p-8">
        <p className="text-muted-foreground">No documents found</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="flex items-center justify-between p-4 rounded-lg border"
        >
          <div>
            <h3 className="font-medium">{doc.title}</h3>
            <div className="flex items-center space-x-2 mt-1">
              <span className="text-sm text-muted-foreground">
                {(doc.file_size / 1024 / 1024).toFixed(2)} MB
              </span>
              <span className="text-muted-foreground">•</span>
              <span className="text-sm text-muted-foreground">
                {formatDistanceToNow(new Date(doc.created_at), {
                  addSuffix: true,
                })}
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {doc.processing_tasks.length > 0 && (
              <Badge
                variant={
                  doc.processing_tasks[0].status === "completed"
                    ? "default"
                    : doc.processing_tasks[0].status === "failed"
                    ? "destructive"
                    : "secondary"
                }
              >
                {doc.processing_tasks[0].status}
              </Badge>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
