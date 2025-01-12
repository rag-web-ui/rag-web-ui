"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { formatDistanceToNow } from "date-fns";
import { api, ApiError } from "@/lib/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

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
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Title</TableHead>
          <TableHead>Size</TableHead>
          <TableHead>Created</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {documents.map((doc) => (
          <TableRow key={doc.id}>
            <TableCell className="font-medium">{doc.title}</TableCell>
            <TableCell>{(doc.file_size / 1024 / 1024).toFixed(2)} MB</TableCell>
            <TableCell>
              {formatDistanceToNow(new Date(doc.created_at), {
                addSuffix: true,
              })}
            </TableCell>
            <TableCell>
              {doc.processing_tasks.length > 0 && (
                <Badge
                  variant={
                    doc.processing_tasks[0].status === "completed"
                      ? "secondary" // Green for completed
                      : doc.processing_tasks[0].status === "failed"
                      ? "destructive" // Red for failed
                      : "default" // Default for pending/processing
                  }
                >
                  {doc.processing_tasks[0].status}
                </Badge>
              )}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
