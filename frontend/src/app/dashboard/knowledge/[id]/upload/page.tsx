"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useDropzone } from "react-dropzone";
import {
  Upload,
  X,
  FileText,
  CheckCircle,
  AlertCircle,
  Loader2,
} from "lucide-react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import { api, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";

interface FileStatus {
  file: File;
  status:
    | "pending"
    | "uploading"
    | "uploaded"
    | "processing"
    | "completed"
    | "error";
  error?: string;
  uploadId?: number;
  taskId?: number;
  documentId?: number;
}

interface UploadResult {
  upload_id?: number;
  document_id?: number;
  file_name: string;
  status: string;
  skip_processing: boolean;
  message?: string;
}

interface ProcessingTask {
  upload_id: number;
  task_id: number;
}

interface TaskStatus {
  document_id: number | null;
  status: string;
  error_message: string | null;
  upload_id: number;
  file_name: string;
}

export default function UploadPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [files, setFiles] = useState<FileStatus[]>([]);
  const [processingTasks, setProcessingTasks] = useState<ProcessingTask[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const { toast } = useToast();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map((file) => ({
      file,
      status: "pending" as const,
    }));
    setFiles((prev) => [...prev, ...newFiles]);

    // Upload each file
    newFiles.forEach(async (fileStatus) => {
      setFiles((prev) =>
        prev.map((f) =>
          f.file === fileStatus.file ? { ...f, status: "uploading" } : f
        )
      );
      await handleUpload(fileStatus.file);
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/plain": [".txt"],
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
      "text/markdown": [".md"],
    },
  });

  const handleUpload = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const result: UploadResult = await api.post(
        `http://localhost:8000/api/knowledge-base/${params.id}/documents/upload`,
        formData
      );

      setFiles((prev) =>
        prev.map((f) =>
          f.file.name === result.file_name
            ? {
                ...f,
                status: result.skip_processing ? "completed" : "uploaded",
                uploadId: result.upload_id,
                documentId: result.document_id,
              }
            : f
        )
      );

      toast({
        title: "Success",
        description: result.message || "File uploaded successfully",
      });
    } catch (error) {
      console.error("Failed to upload file:", error);
      setFiles((prev) =>
        prev.map((f) =>
          f.file === file
            ? {
                ...f,
                status: "error",
                error:
                  error instanceof ApiError ? error.message : "Upload failed",
              }
            : f
        )
      );
    }
  };

  const startProcessing = async () => {
    const uploadedFiles = files.filter((f) => f.status === "uploaded");
    if (uploadedFiles.length === 0) return;

    setIsProcessing(true);
    try {
      const uploadResults = uploadedFiles.map((f) => ({
        upload_id: f.uploadId,
        file_name: f.file.name,
        skip_processing: false,
      }));

      const response = await api.post(
        `http://localhost:8000/api/knowledge-base/${params.id}/documents/process`,
        uploadResults
      );

      setProcessingTasks(response.tasks);

      // Update file statuses to processing
      setFiles((prev) =>
        prev.map((f) => {
          const task = response.tasks.find(
            (t: ProcessingTask) => t.upload_id === f.uploadId
          );
          if (task) {
            return {
              ...f,
              status: "processing",
              taskId: task.task_id,
            };
          }
          return f;
        })
      );
    } catch (error) {
      console.error("Failed to start processing:", error);
      toast({
        title: "Error",
        description: "Failed to start processing files",
        variant: "destructive",
      });
    }
  };

  const checkProcessingStatus = async () => {
    if (processingTasks.length === 0) return;

    try {
      const taskIds = processingTasks.map((t) => t.task_id).join(",");
      const status: Record<string, TaskStatus> = await api.get(
        `http://localhost:8000/api/knowledge-base/${params.id}/documents/tasks?task_ids=${taskIds}`
      );

      let allCompleted = true;
      setFiles((prev) =>
        prev.map((f) => {
          const task = processingTasks.find((t) => t.upload_id === f.uploadId);
          if (task && status[task.task_id]) {
            const taskStatus = status[task.task_id];
            if (taskStatus.status !== "completed") {
              allCompleted = false;
            }
            return {
              ...f,
              status:
                taskStatus.status === "completed"
                  ? "completed"
                  : taskStatus.status === "failed"
                  ? "error"
                  : "processing",
              documentId: taskStatus.document_id || undefined,
              error: taskStatus.error_message || undefined,
            };
          }
          return f;
        })
      );

      if (allCompleted) {
        setIsProcessing(false);
        setShowSuccessModal(true);
        toast({
          title: "Success",
          description: "All files have been processed successfully",
          duration: Infinity,
        });
      }
    } catch (error) {
      console.error("Failed to check processing status:", error);
    }
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isProcessing) {
      interval = setInterval(checkProcessingStatus, 2000);
    }
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [isProcessing, processingTasks]);

  const removeFile = (file: File) => {
    setFiles((prev) => prev.filter((f) => f.file !== file));
  };

  const allCompleted =
    files.length > 0 &&
    files.every((f) => f.status === "completed" || f.status === "error");

  const hasUploadedFiles = files.some((f) => f.status === "uploaded");
  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">
            Upload Documents
          </h2>
          <p className="text-muted-foreground">
            Upload documents to your knowledge base
          </p>
        </div>

        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
            isDragActive
              ? "border-primary bg-primary/5"
              : "border-border hover:border-primary/50"
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-muted-foreground" />
          <p className="mt-4 text-sm text-muted-foreground">
            Drag and drop files here, or click to select files
          </p>
          <p className="mt-2 text-xs text-muted-foreground">
            Supported formats: PDF, DOCX, TXT, MD
          </p>
        </div>

        {files.length > 0 && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Files</h3>
              {hasUploadedFiles && !isProcessing && (
                <button
                  onClick={startProcessing}
                  className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
                >
                  Start Processing
                </button>
              )}
            </div>

            <div className="space-y-2 max-h-[400px] overflow-y-auto rounded-lg">
              {files.map((fileStatus) => (
                <div
                  key={fileStatus.file.name}
                  className="flex items-center justify-between p-4 rounded-lg border bg-card"
                >
                  <div className="flex items-center space-x-4">
                    <FileText className="h-8 w-8 text-primary" />
                    <div>
                      <p className="font-medium">{fileStatus.file.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {(fileStatus.file.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    {fileStatus.status === "uploading" && (
                      <div className="flex items-center space-x-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="text-muted-foreground">
                          Uploading...
                        </span>
                      </div>
                    )}
                    {fileStatus.status === "processing" && (
                      <div className="flex items-center space-x-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="text-muted-foreground">
                          Processing...
                        </span>
                      </div>
                    )}
                    {fileStatus.status === "completed" && (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    )}
                    {fileStatus.status === "error" && (
                      <div className="flex items-center space-x-2 text-red-500">
                        <AlertCircle className="h-5 w-5" />
                        <span className="text-sm">{fileStatus.error}</span>
                      </div>
                    )}
                    <button
                      onClick={() => removeFile(fileStatus.file)}
                      className="p-1 hover:bg-accent rounded-full"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex justify-end space-x-4">
          {showSuccessModal ? (
            <button
              onClick={() => router.push(`/dashboard/knowledge/${params.id}`)}
              className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
            >
              Done
            </button>
          ) : (
            <button
              onClick={() => router.push(`/dashboard/knowledge/${params.id}`)}
              className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
            >
              Cancel
            </button>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
