"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { Loader2, Upload, X, Settings, FileText } from "lucide-react";
import { cn } from "@/lib/utils";
import { api, ApiError } from "@/lib/api";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { useDropzone } from "react-dropzone";

interface DocumentVideoUploadStepsProps {
  knowledgeBaseId: number;
  onComplete?: () => void;
}

interface FileStatus {
  url: string;
  status:
    | "pending"
    | "uploading"
    | "uploaded"
    | "processing"
    | "completed"
    | "error";
  uploadId?: number;
  documentId?: number;
  tempPath?: string;
  error?: string;
}

interface UploadResult {
  upload_id?: number;
  document_id?: number;
  file_name: string;
  status: "exists" | "pending";
  message?: string;
  skip_processing: boolean;
  temp_path?: string;
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
    upload_id: number;
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

interface VideoFile {
  file: File;
  status: "pending" | "uploading" | "uploaded" | "transcribing" | "completed" | "error";
  uploadId?: number;
  documentId?: number;
  tempPath?: string;
  error?: string;
}

export function DocumentVideoUploadSteps({
  knowledgeBaseId,
  onComplete,
}: DocumentVideoUploadStepsProps) {
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
  const [videoUrls, setVideoUrls] = useState("");
  const [uploadMethod, setUploadMethod] = useState<"url" | "file">("url");
  const [videoFiles, setVideoFiles] = useState<VideoFile[]>([]);
  const { toast } = useToast();

  const removeFile = (url: string) => {
    setFiles((prev) => prev.filter((f) => f.url !== url));
  };

  // Add dropzone for video files
  const onDrop = useCallback((acceptedFiles: File[]) => {
    setVideoFiles((prev) => [
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
      "video/mp4": [".mp4"],
      "video/avi": [".avi"],
      "video/mov": [".mov"],
      "video/wmv": [".wmv"],
      "video/webm": [".webm"],
    },
  });

  // Handle video file upload
  const handleVideoFileUpload = async () => {
    const pendingFiles = videoFiles.filter((f) => f.status === "pending");
    if (pendingFiles.length === 0) return;

    setIsLoading(true);
    try {
      const formData = new FormData();
      pendingFiles.forEach((videoFile) => {
        formData.append("files", videoFile.file);
      });

      const data = await api.post(
        `/api/knowledge-base/${knowledgeBaseId}/videos/upload-files`,
        formData
      );

      setVideoFiles((prev) =>
        prev.map((f) => {
          const uploadResult = data.find((d: any) => d.file_name === f.file.name);
          if (uploadResult) {
            return {
              ...f,
              status: "uploaded",
              uploadId: uploadResult.upload_id,
              tempPath: uploadResult.temp_path,
            };
          }
          return f;
        })
      );

      setCurrentStep(2);
      toast({
        title: "Upload successful",
        description: `${data.length} videos uploaded successfully.`,
      });
    } catch (error) {
      toast({
        title: "Upload failed",
        description: error instanceof ApiError ? error.message : "Something went wrong",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Step 1: Upload video URLs
  const handleUrlUpload = async () => {
    const urls = videoUrls
      .split("\n")
      .map((url) => url.trim())
      .filter((url) => url);

    if (urls.length === 0) return;

    setIsLoading(true);
    try {
      const data = (await api.post(
        `/api/knowledge-base/${knowledgeBaseId}/videos/upload`,
        { urls }
      )) as UploadResult[];

      setFiles(
        data.map((uploadResult) => ({
          url: uploadResult.file_name,
          status: uploadResult.status === "exists" ? "completed" : "uploaded",
          uploadId: uploadResult.upload_id,
          documentId: uploadResult.document_id,
          tempPath: uploadResult.temp_path,
          error: uploadResult.message,
        }))
      );
      setCurrentStep(2);
      toast({
        title: "Upload successful",
        description: `${data.length} videos uploaded successfully.`,
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
    const selectedFile = files.find(
      (f) =>
        f.documentId === selectedDocumentId || f.uploadId === selectedDocumentId
    );
    if (!selectedFile) return;

    setIsLoading(true);
    try {
      const data = await api.post(
        `/api/knowledge-base/${knowledgeBaseId}/videos/preview`,
        {
          document_ids: [selectedDocumentId],
          chunk_size: chunkSize,
          chunk_overlap: chunkOverlap,
        }
      );

      setUploadedDocuments(data);

      toast({
        title: "Preview generated",
        description: "Video preview generated successfully.",
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

  // Step 3: Process videos
  const handleProcess = async (uploadResults?: UploadResult[]) => {
    const resultsToProcess =
      uploadResults ||
      files
        .filter((f) => f.status === "uploaded")
        .map((f) => ({
          upload_id: f.uploadId!,
          file_name: f.url,
          status: "pending" as const,
          skip_processing: false,
          temp_path: f.tempPath!,
        }));

    if (resultsToProcess.length === 0) return;

    setIsLoading(true);
    try {
      const data = (await api.post(
        `/api/knowledge-base/${knowledgeBaseId}/videos/process`,
        resultsToProcess
      )) as TaskResponse;

      // Initialize task statuses
      const initialStatuses = data.tasks.reduce<TaskStatusMap>(
        (acc, task) => ({
          ...acc,
          [task.task_id]: {
            document_id: task.upload_id,
            status: "pending" as const,
          },
        }),
        {}
      );
      setTaskStatuses(initialStatuses);

      // Start polling for task status
      pollTaskStatus(data.tasks.map((t) => t.task_id));
    } catch (error) {
      setIsLoading(false);
      toast({
        title: "Processing failed",
        description:
          error instanceof ApiError ? error.message : "Something went wrong",
        variant: "destructive",
      });
    }
  };

  // Poll task status
  const pollTaskStatus = async (taskIds: number[]) => {
    const poll = async () => {
      try {
        const response = (await api.get(
          `/api/knowledge-base/${knowledgeBaseId}/videos/tasks?task_ids=${taskIds.join(
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
          (task) => task.status === "completed" || task.status === "failed"
        );

        if (allDone) {
          setIsLoading(false);
          const hasErrors = Object.values(data).some(
            (task) => task.status === "failed"
          );
          if (!hasErrors) {
            toast({
              title: "Processing completed",
              description: "All videos have been processed successfully.",
            });
            onComplete?.();
          } else {
            toast({
              title: "Processing completed with errors",
              description: "Some videos failed to process.",
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

  const handleProcessClick = (e: React.MouseEvent) => {
    e.preventDefault();
    handleProcess();
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="mb-8">
        <div className="flex justify-between mb-2">
          {[
            { step: 1, icon: Upload, label: "Upload" },
            { step: 2, icon: FileText, label: "Preview" },
            { step: 3, icon: Settings, label: "Process" },
          ].map(({ step, icon: Icon, label }, index, array) => (
            <div
              key={step}
              className="flex flex-col items-center space-y-2 flex-1"
            >
              <div
                className={cn(
                  "w-12 h-12 rounded-full flex items-center justify-center border-2 transition-colors",
                  currentStep === step
                    ? "bg-primary text-primary-foreground border-primary"
                    : currentStep > step
                    ? "bg-primary/20 border-primary/20"
                    : "bg-background border-input"
                )}
              >
                <Icon className="w-6 h-6" />
              </div>
              <span className="text-sm font-medium">
                {step}. {label}
              </span>
              {index < array.length - 1 && (
                <div
                  className={cn(
                    "h-0.5 w-full mt-2",
                    currentStep > step ? "bg-primary/20" : "bg-input"
                  )}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      <Tabs value={String(currentStep)} className="w-full">
        <TabsContent value="1" className="mt-6">
          <Card className="p-6">
            <div className="space-y-4">
              {/* Upload method selector */}
              <div className="flex space-x-4 mb-4">
                <Button
                  variant={uploadMethod === "url" ? "default" : "outline"}
                  onClick={() => setUploadMethod("url")}
                >
                  Upload by URL
                </Button>
                <Button
                  variant={uploadMethod === "file" ? "default" : "outline"}
                  onClick={() => setUploadMethod("file")}
                >
                  Upload Files
                </Button>
              </div>

              {uploadMethod === "url" ? (
                // Existing URL upload UI
                <div>
                  <label htmlFor="video-urls" className="block mb-2 font-medium">
                    Nhập đường dẫn video (mỗi dòng một link)
                  </label>
                  <textarea
                    id="video-urls"
                    rows={6}
                    className="w-full border rounded-lg p-2"
                    placeholder="https://example.com/video1.mp4&#10;https://example.com/video2.mp4"
                    value={videoUrls}
                    onChange={(e) => setVideoUrls(e.target.value)}
                  />
                  <Button
                    onClick={handleUrlUpload}
                    disabled={!videoUrls.trim() || isLoading}
                    className="w-full mt-4"
                  >
                    {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Upload Videos
                  </Button>
                </div>
              ) : (
                // New file upload UI
                <div>
                  <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                      isDragActive ? "border-primary bg-primary/5" : "border-gray-300"
                    }`}
                  >
                    <input {...getInputProps()} />
                    <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                    <p className="text-lg font-medium mb-2">
                      {isDragActive ? "Drop videos here" : "Upload video files"}
                    </p>
                    <p className="text-sm text-gray-500">
                      Drag & drop video files or click to browse
                    </p>
                    <p className="text-xs text-gray-400 mt-2">
                      Supported: MP4, AVI, MOV, WMV, WebM
                    </p>
                  </div>

                  {videoFiles.length > 0 && (
                    <div className="space-y-2 max-h-[300px] overflow-y-auto mt-4">
                      {videoFiles.map((videoFile, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-4 rounded-lg border"
                        >
                          <div>
                            <p className="text-sm font-medium">{videoFile.file.name}</p>
                            <p className="text-xs text-gray-500">
                              {(videoFile.file.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            {videoFile.status === "uploaded" && (
                              <span className="text-green-500 text-sm">Uploaded</span>
                            )}
                            {videoFile.status === "error" && (
                              <span className="text-red-500 text-sm">{videoFile.error}</span>
                            )}
                            <button
                              onClick={() => setVideoFiles(prev => prev.filter((_, i) => i !== index))}
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
                    onClick={handleVideoFileUpload}
                    disabled={videoFiles.filter(f => f.status === "pending").length === 0 || isLoading}
                    className="w-full mt-4"
                  >
                    {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Upload Videos
                  </Button>
                </div>
              )}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="2" className="mt-6">
          <Card className="p-6">
            <div className="space-y-6">
              <h3 className="text-lg font-medium">
                Select Video to Preview
              </h3>
              <div className="flex items-center space-x-4">
                <Select
                  value={selectedDocumentId?.toString()}
                  onValueChange={(value: string) =>
                    setSelectedDocumentId(parseInt(value))
                  }
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select a video to preview" />
                  </SelectTrigger>
                  <SelectContent>
                    {files
                      .filter((f) => f.status === "uploaded")
                      .map((f) => (
                        <SelectItem
                          key={f.uploadId}
                          value={f.uploadId?.toString() || ""}
                        >
                          {f.url}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>

              <Accordion type="single" collapsible className="w-full">
                <AccordionItem value="settings">
                  <AccordionTrigger>Advanced Settings</AccordionTrigger>
                  <AccordionContent>
                    <div className="grid gap-4 md:grid-cols-2 pt-4">
                      <div className="space-y-2">
                        <Label htmlFor="chunk-size">Chunk Size (tokens)</Label>
                        <Input
                          id="chunk-size"
                          type="number"
                          value={chunkSize}
                          onChange={(e) =>
                            setChunkSize(parseInt(e.target.value))
                          }
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="chunk-overlap">
                          Chunk Overlap (tokens)
                        </Label>
                        <Input
                          id="chunk-overlap"
                          type="number"
                          value={chunkOverlap}
                          onChange={(e) =>
                            setChunkOverlap(parseInt(e.target.value))
                          }
                        />
                      </div>
                    </div>
                  </AccordionContent>
                </AccordionItem>
              </Accordion>

              <div className="flex space-x-4">
                <Button
                  onClick={handlePreview}
                  disabled={isLoading || !selectedDocumentId}
                  className="flex-1"
                >
                  {isLoading && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  Preview Chunks
                </Button>
                <Button
                  onClick={() => setCurrentStep(3)}
                  variant="secondary"
                  className="flex-1"
                >
                  Continue
                </Button>
              </div>

              {selectedDocumentId && uploadedDocuments[selectedDocumentId] && (
                <div className="space-y-4">
                  <div className="mt-4">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium">
                        {
                          files.find((f) => f.uploadId === selectedDocumentId)
                            ?.url
                        }
                      </h3>
                      <span className="text-sm text-muted-foreground">
                        {uploadedDocuments[selectedDocumentId].chunks.length}{" "}
                        chunks
                      </span>
                    </div>
                    <div className="h-[400px] overflow-y-auto space-y-2 rounded-lg border p-4">
                      {uploadedDocuments[selectedDocumentId].chunks.map(
                        (chunk: PreviewChunk, index: number) => (
                          <div
                            key={index}
                            className="p-4 bg-muted rounded-lg space-y-2"
                          >
                            <div className="text-sm text-muted-foreground">
                              Chunk {index + 1}
                            </div>
                            <pre className="whitespace-pre-wrap text-sm">
                              {chunk.content}
                            </pre>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </Card>
        </TabsContent>
        <TabsContent value="3" className="mt-6">
          <Card className="p-6">
            <div className="space-y-4">
              <div className="max-h-[300px] overflow-y-auto space-y-2 rounded-lg border p-4">
                {files
                  .filter((f) => f.status === "uploaded")
                  .map((file) => {
                    const task = Object.values(taskStatuses).find(
                      (t) => t.document_id === file.documentId
                    );
                    return (
                      <div
                        key={file.uploadId}
                        className="p-4 border rounded-lg space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium">
                              {file.url}
                            </p>
                            {task && (
                              <p className="text-xs text-muted-foreground">
                                Status: {task.status || "pending"}
                              </p>
                            )}
                          </div>
                          {task?.status === "failed" && (
                            <p className="text-sm text-destructive">
                              {task.error_message}
                            </p>
                          )}
                        </div>
                        {task &&
                          (task.status === "pending" ||
                            task.status === "processing") && (
                            <Progress
                              value={task.status === "processing" ? 50 : 25}
                              className="w-full"
                            />
                          )}
                      </div>
                    );
                  })}
              </div>

              <Button
                onClick={handleProcessClick}
                disabled={
                  isLoading ||
                  files.filter((f) => f.status === "uploaded").length === 0
                }
                className="w-full"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Settings className="mr-2 h-4 w-4" />
                    Process
                  </>
                )}
              </Button>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
