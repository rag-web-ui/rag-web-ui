"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { formatDistanceToNow } from "date-fns";
import { api, ApiError } from "@/lib/api";
import { FileIcon, defaultStyles } from "react-file-icon";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { FileText } from "lucide-react";

interface Document {
  id: number;
  file_name: string;
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
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const data = await api.get(
          `http://localhost:8000/api/knowledge-base/${knowledgeBaseId}`
        );
        setDocuments(data.documents);
      } catch (error) {
        if (error instanceof ApiError) {
          setError(error.message);
        } else {
          setError("Failed to fetch documents");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, [knowledgeBaseId]);

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="space-y-4">
          <div className="w-8 h-8 border-4 border-primary/30 border-t-primary rounded-full animate-spin mx-auto"></div>
          <p className="text-muted-foreground animate-pulse">
            Loading documents...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center p-8">
        <p className="text-destructive">{error}</p>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] p-8">
        <div className="flex flex-col items-center max-w-[420px] text-center space-y-6">
          <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center">
            <FileText className="w-10 h-10 text-muted-foreground" />
          </div>
          <div className="space-y-2">
            <h3 className="text-xl font-semibold">No documents yet</h3>
            <p className="text-muted-foreground">
              Upload your first document to start building your knowledge base.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Size</TableHead>
          <TableHead>Created</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {documents.map((doc) => (
          <TableRow key={doc.id}>
            <TableCell className="font-medium">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6">
                  {doc.content_type.toLowerCase().includes("pdf") ? (
                    <FileIcon extension="pdf" {...defaultStyles.pdf} />
                  ) : doc.content_type.toLowerCase().includes("doc") ? (
                    <FileIcon extension="doc" {...defaultStyles.docx} />
                  ) : doc.content_type.toLowerCase().includes("txt") ? (
                    <FileIcon extension="txt" {...defaultStyles.txt} />
                  ) : doc.content_type.toLowerCase().includes("md") ? (
                    <FileIcon extension="md" {...defaultStyles.md} />
                  ) : (
                    <FileIcon
                      extension={doc.file_name.split(".").pop() || ""}
                      color="#E2E8F0"
                      labelColor="#94A3B8"
                    />
                  )}
                </div>
                {doc.file_name}
              </div>
            </TableCell>
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
