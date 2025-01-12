"use client";

import { useEffect, useState } from "react";
import { FileIcon, defaultStyles } from "react-file-icon";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { formatDistanceToNow } from "date-fns";

interface Document {
  id: number;
  title: string;
  file_size: number;
  content_type: string;
  created_at: string;
  processing_tasks: Array<{
    id: number;
    status: "pending" | "processing" | "completed" | "failed";
    error_message?: string;
  }>;
}

interface DocumentListProps {
  knowledgeBaseId: number;
}

export function DocumentList({ knowledgeBaseId }: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(
          `http://localhost:8000/api/knowledge-base/${knowledgeBaseId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        if (!response.ok) throw new Error("Failed to fetch documents");
        const data = await response.json();
        setDocuments(data.documents || []);
      } catch (error) {
        console.error("Error fetching documents:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDocuments();
  }, [knowledgeBaseId]);

  const formatFileSize = (bytes: number) => {
    const units = ["B", "KB", "MB", "GB"];
    let size = bytes;
    let unitIndex = 0;

    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }

    return `${size.toFixed(1)} ${units[unitIndex]}`;
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-500";
      case "processing":
        return "bg-blue-500";
      case "failed":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-muted-foreground">Loading documents...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Title</TableHead>
            <TableHead>Size</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Added</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {documents.map((doc) => (
            <TableRow key={doc.id}>
              <TableCell className="font-medium">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 flex-shrink-0">
                    {doc.content_type.toLowerCase().includes("pdf") ? (
                      <FileIcon extension="pdf" {...defaultStyles.pdf} />
                    ) : doc.content_type.toLowerCase().includes("doc") ? (
                      <FileIcon extension="doc" {...defaultStyles.docx} />
                    ) : doc.content_type.toLowerCase().includes("txt") ? (
                      <FileIcon extension="txt" {...defaultStyles.txt} />
                    ) : (
                      <FileIcon
                        extension=""
                        color="#E2E8F0"
                        labelColor="#94A3B8"
                        labelTextColor="#1E293B"
                        type="document"
                      />
                    )}
                  </div>
                  {doc.title}
                </div>
              </TableCell>
              <TableCell>{formatFileSize(doc.file_size)}</TableCell>
              <TableCell>{doc.content_type}</TableCell>
              <TableCell>
                {doc.processing_tasks?.length > 0 ? (
                  <Badge
                    className={getStatusBadgeColor(
                      doc.processing_tasks[0].status
                    )}
                  >
                    {doc.processing_tasks[0].status}
                  </Badge>
                ) : (
                  <Badge variant="secondary">No status</Badge>
                )}
              </TableCell>
              <TableCell>
                {formatDistanceToNow(new Date(doc.created_at), {
                  addSuffix: true,
                })}
              </TableCell>
            </TableRow>
          ))}
          {documents.length === 0 && (
            <TableRow>
              <TableCell
                colSpan={5}
                className="text-center text-muted-foreground"
              >
                No documents found
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
