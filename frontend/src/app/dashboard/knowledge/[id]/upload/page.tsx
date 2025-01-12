"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useDropzone } from "react-dropzone";
import { Upload, X, FileText, CheckCircle, AlertCircle } from "lucide-react";
import DashboardLayout from "@/components/layout/dashboard-layout";
import { api, ApiError } from "@/lib/utils";
import { useToast } from "@/components/ui/use-toast";

interface FileStatus {
  file: File;
  status: "pending" | "uploading" | "success" | "error";
  error?: string;
}

export default function UploadPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [files, setFiles] = useState<FileStatus[]>([]);
  const { toast } = useToast();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prev) => [
      ...prev,
      ...acceptedFiles.map((file) => ({
        file,
        status: "pending" as const,
      })),
    ]);
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

  const uploadFile = async (fileStatus: FileStatus) => {
    const formData = new FormData();
    formData.append("file", fileStatus.file);

    try {
      await api.post(
        `http://localhost:8000/api/knowledge-base/${params.id}/upload`,
        formData,
        {
          // Don't set Content-Type header, let the browser set it with the boundary
          headers: {},
        }
      );

      setFiles((prev) =>
        prev.map((f) =>
          f.file === fileStatus.file ? { ...f, status: "success" } : f
        )
      );

      toast({
        title: "Success",
        description: `${fileStatus.file.name} uploaded successfully`,
      });
    } catch (error) {
      const errorMessage =
        error instanceof ApiError ? error.message : "Upload failed";
      setFiles((prev) =>
        prev.map((f) =>
          f.file === fileStatus.file
            ? {
                ...f,
                status: "error",
                error: errorMessage,
              }
            : f
        )
      );

      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  const uploadAllFiles = async () => {
    const pendingFiles = files.filter((f) => f.status === "pending");
    for (const fileStatus of pendingFiles) {
      setFiles((prev) =>
        prev.map((f) =>
          f.file === fileStatus.file ? { ...f, status: "uploading" } : f
        )
      );
      await uploadFile(fileStatus);
    }
  };

  const removeFile = (file: File) => {
    setFiles((prev) => prev.filter((f) => f.file !== file));
  };

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
              <button
                onClick={uploadAllFiles}
                disabled={!files.some((f) => f.status === "pending")}
                className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
              >
                Upload All
              </button>
            </div>

            <div className="space-y-2">
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
                    {fileStatus.status === "pending" && (
                      <button
                        onClick={() => uploadFile(fileStatus)}
                        className="text-primary hover:text-primary/80"
                      >
                        Upload
                      </button>
                    )}
                    {fileStatus.status === "uploading" && (
                      <span className="text-muted-foreground">
                        Uploading...
                      </span>
                    )}
                    {fileStatus.status === "success" && (
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
          <button
            onClick={() => router.push("/dashboard/knowledge")}
            className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
          >
            Done
          </button>
        </div>
      </div>
    </DashboardLayout>
  );
}
