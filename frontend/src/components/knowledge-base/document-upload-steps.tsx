"use client";

import { useState, useCallback } from "react";
import { FileIcon, defaultStyles } from "react-file-icon";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { Loader2, Upload, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { api, ApiError } from "@/lib/api";
import { useDropzone } from "react-dropzone";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface DocumentUploadStepsProps {
  knowledgeBaseId: number;
  onComplete?: () => void;
}

interface FileStatus {
  file: File;
  status: "pending" | "uploading" | "uploaded" | "error";
  documentId?: number;
  filePath?: string;
  error?: string;
}

interface UploadResult {
  file_name: string;
  document_id: number;
  file_path: string;
  is_duplicate: boolean;
}

interface PreviewChunk {
  content: string;
  metadata: Record<string, any>;
}

interface PreviewResponse {
  chunks: PreviewChunk[];
  total_chunks: number;
}

interface TaskResponse {
  tasks: Array<{
    document_id: number;
    task_id: number;
  }>;
}

interface TaskStatus {
  document_id: number;
  status: "pending" | "processing" | "completed" | "failed";
  error_message?: string;
}

interface TaskStatusMap {
  [key: number]: TaskStatus;
}

interface TaskStatusResponse {
  [key: string]: TaskStatus;
}

export function DocumentUploadSteps({
  knowledgeBaseId,
  onComplete,
}: DocumentUploadStepsProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [files, setFiles] = useState<FileStatus[]>([]);
  const [uploadedDocuments, setUploadedDocuments] = useState<{
    [key: number]: PreviewResponse;
  }>({});
  const [selectedDocumentId, setSelectedDocumentId] = useState<number | null>(
    null
  );
  const [taskStatuses, setTaskStatuses] = useState<{
    [key: number]: TaskStatus;
  }>({});
  const [isLoading, setIsLoading] = useState(false);
  const [chunkSize, setChunkSize] = useState(1000);
  const [chunkOverlap, setChunkOverlap] = useState(200);
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
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
      "text/plain": [".txt"],
      "text/markdown": [".md"],
    },
  });

  const removeFile = (file: File) => {
    setFiles((prev) => prev.filter((f) => f.file !== file));
  };

  // Step 1: Upload files
  const handleFileUpload = async () => {
    const pendingFiles = files.filter((f) => f.status === "pending");
    if (pendingFiles.length === 0) return;

    setIsLoading(true);
    try {
      const formData = new FormData();
      pendingFiles.forEach((fileStatus) => {
        formData.append("files", fileStatus.file);
      });

      const data = (await api.post(
        `http://localhost:8000/api/knowledge-base/${knowledgeBaseId}/documents/upload`,
        formData,
        {
          headers: {},
        }
      )) as UploadResult[];

      // Update file statuses
      setFiles((prev) =>
        prev.map((f) => {
          const uploadResult = data.find((d) => d.file_name === f.file.name);
          if (uploadResult) {
            return {
              ...f,
              status: "uploaded",
              documentId: uploadResult.document_id,
              filePath: uploadResult.file_path,
            };
          }
          return f;
        })
      );

      // Set the first document as selected by default
      const firstUploadedFile = data[0];
      if (firstUploadedFile) {
        setSelectedDocumentId(firstUploadedFile.document_id);
      }

      setCurrentStep(2);
      toast({
        title: "Upload successful",
        description: `${data.length} files uploaded successfully.`,
      });
    } catch (error) {
      toast({
        title: "Upload failed",
        description:
          error instanceof ApiError ? error.message : "Something went wrong",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Step 2: Preview chunks
  const handlePreview = async () => {
    if (!selectedDocumentId) return;

    setIsLoading(true);
    try {
      const data = await api.post(
        `http://localhost:8000/api/knowledge-base/${knowledgeBaseId}/documents/preview`,
        [selectedDocumentId]
      );

      setUploadedDocuments(data);

      toast({
        title: "Preview generated",
        description: "Document preview generated successfully.",
      });
    } catch (error) {
      toast({
        title: "Preview failed",
        description:
          error instanceof ApiError ? error.message : "Something went wrong",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Step 3: Process documents
  const handleProcess = async () => {
    const uploadedFiles = files.filter((f) => f.status === "uploaded");
    if (uploadedFiles.length === 0) return;

    setIsLoading(true);
    try {
      const documentIds = uploadedFiles.map((f) => f.documentId!);
      const data = (await api.post(
        `http://localhost:8000/api/knowledge-base/${knowledgeBaseId}/documents/process`,
        documentIds
      )) as TaskResponse;

      // Initialize task statuses
      const initialStatuses = data.tasks.reduce<TaskStatusMap>(
        (
          acc: TaskStatusMap,
          task: { document_id: number; task_id: number }
        ) => ({
          ...acc,
          [task.task_id]: {
            document_id: task.document_id,
            status: "pending" as const,
          },
        }),
        {}
      );
      setTaskStatuses(initialStatuses);

      // Start polling for task status
      pollTaskStatus(data.tasks.map((t: { task_id: number }) => t.task_id));
    } catch (error) {
      toast({
        title: "Processing failed",
        description:
          error instanceof ApiError ? error.message : "Something went wrong",
        variant: "destructive",
      });
      setIsLoading(false);
    }
  };

  // Poll task status
  const pollTaskStatus = async (taskIds: number[]) => {
    const poll = async () => {
      try {
        const response = (await api.get(
          `http://localhost:8000/api/knowledge-base/${knowledgeBaseId}/documents/tasks?task_ids=${taskIds.join(
            ","
          )}`
        )) as TaskStatusResponse;

        // Convert string keys to numbers
        const data = Object.entries(response).reduce<TaskStatusMap>(
          (acc, [key, value]) => ({
            ...acc,
            [parseInt(key)]: value,
          }),
          {}
        );

        setTaskStatuses(data);

        // Check if all tasks are completed or failed
        const allDone = Object.values(data).every(
          (task: TaskStatus) =>
            task.status === "completed" || task.status === "failed"
        );

        if (allDone) {
          setIsLoading(false);
          const hasErrors = Object.values(data).some(
            (task: TaskStatus) => task.status === "failed"
          );
          if (!hasErrors) {
            toast({
              title: "Processing completed",
              description: "All documents have been processed successfully.",
            });
            onComplete?.();
          } else {
            toast({
              title: "Processing completed with errors",
              description: "Some documents failed to process.",
              variant: "destructive",
            });
          }
        } else {
          // Continue polling
          setTimeout(poll, 2000);
        }
      } catch (error) {
        setIsLoading(false);
        toast({
          title: "Status check failed",
          description:
            error instanceof ApiError ? error.message : "Something went wrong",
          variant: "destructive",
        });
      }
    };

    poll();
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="mb-8">
        <div className="flex justify-between mb-2 px-4">
          {[1, 2, 3].map((step) => (
            <div
              key={step}
              className={cn("flex items-center", step < 3 && "flex-1")}
            >
              <div
                className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center border",
                  currentStep === step
                    ? "bg-primary text-primary-foreground border-primary"
                    : currentStep > step
                    ? "bg-primary/20 border-primary/20"
                    : "bg-background border-input"
                )}
              >
                {step}
              </div>
              {step < 3 && (
                <div
                  className={cn(
                    "h-1 flex-1 mx-2",
                    currentStep > step ? "bg-primary/20" : "bg-input"
                  )}
                />
              )}
            </div>
          ))}
        </div>
        <div className="flex justify-between">
          <span className="text-sm">Upload</span>
          <span className="text-sm">Preview</span>
          <span className="text-sm">Process</span>
        </div>
      </div>

      <Tabs value={String(currentStep)} className="w-full">
        <TabsContent value="1" className="mt-6">
          <Card className="p-6">
            <div className="space-y-4">
              <div
                {...getRootProps()}
                className={cn(
                  "border-2 border-dashed rounded-lg p-8 text-center transition-colors",
                  isDragActive
                    ? "border-primary bg-primary/5"
                    : "hover:border-primary/50"
                )}
              >
                <input {...getInputProps()} />
                <Upload className="w-12 h-12 mx-auto text-muted-foreground" />
                <p className="mt-2 text-sm font-medium">
                  Drop your files here or click to browse
                </p>
                <p className="text-xs text-muted-foreground">
                  Supports PDF, DOCX, TXT, and MD files
                </p>
              </div>

              {files.length > 0 && (
                <div className="space-y-2">
                  {files.map((fileStatus) => (
                    <div
                      key={fileStatus.file.name}
                      className="flex items-center justify-between p-4 rounded-lg border"
                    >
                      <div className="flex items-center space-x-4">
                        <div className="w-8 h-8">
                          <FileIcon
                            extension={fileStatus.file.name.split(".").pop()}
                            {...defaultStyles[
                              fileStatus.file.name
                                .split(".")
                                .pop() as keyof typeof defaultStyles
                            ]}
                          />
                        </div>
                        <div>
                          <p className="text-sm font-medium">
                            {fileStatus.file.name}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {(fileStatus.file.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {fileStatus.status === "uploaded" && (
                          <span className="text-green-500 text-sm">
                            Uploaded
                          </span>
                        )}
                        {fileStatus.status === "error" && (
                          <span className="text-red-500 text-sm">
                            {fileStatus.error}
                          </span>
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
              )}

              <Button
                onClick={handleFileUpload}
                disabled={
                  !files.some((f) => f.status === "pending") || isLoading
                }
              >
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Upload Files
              </Button>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="2" className="mt-6">
          <Card className="p-6">
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <Label htmlFor="document-select">Select Document</Label>
                <Select
                  value={selectedDocumentId?.toString()}
                  onValueChange={(value: string) =>
                    setSelectedDocumentId(parseInt(value))
                  }
                >
                  <SelectTrigger className="w-[300px]">
                    <SelectValue placeholder="Select a document to preview" />
                  </SelectTrigger>
                  <SelectContent>
                    {files
                      .filter((f) => f.status === "uploaded")
                      .map((f) => (
                        <SelectItem
                          key={f.documentId}
                          value={f.documentId!.toString()}
                        >
                          {f.file.name}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="chunk-size">Chunk Size (tokens)</Label>
                  <Input
                    id="chunk-size"
                    type="number"
                    value={chunkSize}
                    onChange={(e) => setChunkSize(parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="chunk-overlap">Chunk Overlap (tokens)</Label>
                  <Input
                    id="chunk-overlap"
                    type="number"
                    value={chunkOverlap}
                    onChange={(e) => setChunkOverlap(parseInt(e.target.value))}
                  />
                </div>
              </div>

              <Button
                onClick={handlePreview}
                disabled={isLoading || !selectedDocumentId}
              >
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Generate Preview
              </Button>

              {selectedDocumentId && uploadedDocuments[selectedDocumentId] && (
                <div className="space-y-4">
                  <div className="mt-4">
                    <h3 className="text-lg font-medium mb-2">
                      {
                        files.find((f) => f.documentId === selectedDocumentId)
                          ?.file.name
                      }
                    </h3>
                    <div className="h-[400px] overflow-y-auto space-y-2">
                      {uploadedDocuments[selectedDocumentId].chunks.map(
                        (chunk: PreviewChunk, index: number) => (
                          <Card key={index} className="p-4">
                            <pre className="whitespace-pre-wrap text-sm">
                              {chunk.content}
                            </pre>
                          </Card>
                        )
                      )}
                    </div>
                  </div>

                  <Button onClick={() => setCurrentStep(3)}>Continue</Button>
                </div>
              )}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="3" className="mt-6">
          <Card className="p-6">
            <div className="space-y-4">
              <Button onClick={handleProcess} disabled={isLoading}>
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Start Processing
              </Button>

              {Object.keys(taskStatuses).length > 0 && (
                <div className="space-y-4">
                  {files
                    .filter((f) => f.status === "uploaded")
                    .map((file) => {
                      const task = Object.values(taskStatuses).find(
                        (t) => t.document_id === file.documentId
                      );
                      return (
                        <div
                          key={file.documentId}
                          className="flex items-center justify-between"
                        >
                          <div>
                            <p className="text-sm font-medium">
                              {file.file.name}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              Status: {task?.status || "pending"}
                            </p>
                          </div>
                          {task?.status === "failed" && (
                            <p className="text-sm text-destructive">
                              {task.error_message}
                            </p>
                          )}
                          {(task?.status === "pending" ||
                            task?.status === "processing") && (
                            <Progress
                              value={task?.status === "processing" ? 50 : 25}
                              className="w-1/3"
                            />
                          )}
                        </div>
                      );
                    })}
                </div>
              )}
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
