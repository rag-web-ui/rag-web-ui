"use client";

import { useState } from "react";
import { FileIcon, defaultStyles } from "react-file-icon";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { Loader2, Upload } from "lucide-react";
import { cn } from "@/lib/utils";

interface DocumentUploadStepsProps {
  knowledgeBaseId: number;
  onComplete?: () => void;
}

interface UploadResponse {
  document_id: number;
  file_path: string;
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
  task_id: number;
  status: "pending" | "processing" | "completed" | "failed";
  error_message?: string;
}

export function DocumentUploadSteps({
  knowledgeBaseId,
  onComplete,
}: DocumentUploadStepsProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [file, setFile] = useState<File | null>(null);
  const [uploadResponse, setUploadResponse] = useState<UploadResponse | null>(
    null
  );
  const [previewResponse, setPreviewResponse] =
    useState<PreviewResponse | null>(null);
  const [taskResponse, setTaskResponse] = useState<TaskResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [chunkSize, setChunkSize] = useState(1000);
  const [chunkOverlap, setChunkOverlap] = useState(200);
  const { toast } = useToast();

  // Step 1: Upload file
  const handleFileUpload = async () => {
    if (!file) return;

    setIsLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `http://localhost:8000/api/knowledge-base/${knowledgeBaseId}/document/upload`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );

      if (!response.ok) throw new Error("Upload failed");

      const data = await response.json();
      setUploadResponse(data);
      setCurrentStep(2);
      toast({
        title: "Upload successful",
        description: "File has been uploaded successfully.",
      });
    } catch (error) {
      toast({
        title: "Upload failed",
        description:
          error instanceof Error ? error.message : "Something went wrong",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Step 2: Preview chunks
  const handlePreview = async () => {
    if (!uploadResponse) return;

    setIsLoading(true);
    try {
      const token = localStorage.getItem("token");

      const response = await fetch(
        `http://localhost:8000/api/knowledge-base/${knowledgeBaseId}/document/${uploadResponse.document_id}/preview`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            chunk_size: chunkSize,
            chunk_overlap: chunkOverlap,
          }),
        }
      );

      if (!response.ok) throw new Error("Preview failed");

      const data = await response.json();
      setPreviewResponse(data);
      toast({
        title: "Preview generated",
        description: `Generated ${data.total_chunks} chunks.`,
      });
    } catch (error) {
      toast({
        title: "Preview failed",
        description:
          error instanceof Error ? error.message : "Something went wrong",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Step 3: Process document
  const handleProcess = async () => {
    if (!uploadResponse) return;

    setIsLoading(true);
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `http://localhost:8000/api/knowledge-base/${knowledgeBaseId}/document/${uploadResponse.document_id}/process?` +
          new URLSearchParams({
            chunk_size: chunkSize.toString(),
            chunk_overlap: chunkOverlap.toString(),
          }),
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) throw new Error("Processing failed");

      const data = await response.json();
      setTaskResponse(data);
      pollTaskStatus(data.task_id);
    } catch (error) {
      toast({
        title: "Processing failed",
        description:
          error instanceof Error ? error.message : "Something went wrong",
        variant: "destructive",
      });
      setIsLoading(false);
    }
  };

  // Poll task status
  const pollTaskStatus = async (taskId: number) => {
    if (!uploadResponse) return;

    const poll = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(
          `http://localhost:8000/api/knowledge-base/${knowledgeBaseId}/document/${uploadResponse.document_id}/task/${taskId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) throw new Error("Failed to get task status");

        const data = await response.json();
        setTaskResponse(data);

        if (data.status === "completed") {
          setIsLoading(false);
          toast({
            title: "Processing completed",
            description: "Document has been processed successfully.",
          });
          onComplete?.();
        } else if (data.status === "failed") {
          setIsLoading(false);
          toast({
            title: "Processing failed",
            description: data.error_message || "Something went wrong",
            variant: "destructive",
          });
        } else {
          // Continue polling
          setTimeout(poll, 2000);
        }
      } catch (error) {
        setIsLoading(false);
        toast({
          title: "Status check failed",
          description:
            error instanceof Error ? error.message : "Something went wrong",
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
                className={cn(
                  "border-2 border-dashed rounded-lg p-8 text-center hover:border-primary/50 transition-colors",
                  file && "border-primary/50 bg-primary/5"
                )}
              >
                <Input
                  type="file"
                  className="hidden"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  id="file-upload"
                />
                <Label
                  htmlFor="file-upload"
                  className="flex flex-col items-center gap-2 cursor-pointer"
                >
                  {file ? (
                    <>
                      <div className="w-12 h-12">
                        {file.type.toLowerCase().includes("pdf") ? (
                          <FileIcon extension="pdf" {...defaultStyles.pdf} />
                        ) : file.type.toLowerCase().includes("doc") ? (
                          <FileIcon extension="doc" {...defaultStyles.docx} />
                        ) : file.type.toLowerCase().includes("text") ? (
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
                      <div>
                        <p className="text-sm font-medium">{file.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </>
                  ) : (
                    <>
                      <Upload className="w-12 h-12 text-muted-foreground" />
                      <p className="text-sm font-medium">
                        Drop your file here or click to browse
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Supports PDF, DOC, DOCX, and TXT files
                      </p>
                    </>
                  )}
                </Label>
              </div>
              <Button onClick={handleFileUpload} disabled={!file || isLoading}>
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Upload
              </Button>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="2" className="mt-6">
          <Card className="p-6">
            <div className="space-y-4">
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
              <Button onClick={handlePreview} disabled={isLoading}>
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Generate Preview
              </Button>
              {previewResponse && (
                <div className="mt-4">
                  <h3 className="text-lg font-medium mb-2">Preview</h3>
                  <div className="h-[400px] overflow-y-auto space-y-2">
                    {previewResponse.chunks.map((chunk, index) => (
                      <Card key={index} className="p-4">
                        <pre className="whitespace-pre-wrap text-sm">
                          {chunk.content}
                        </pre>
                      </Card>
                    ))}
                  </div>
                  <Button className="mt-4" onClick={() => setCurrentStep(3)}>
                    Continue
                  </Button>
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
              {taskResponse && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">
                      Status: {taskResponse.status}
                    </span>
                    {(taskResponse.status === "pending" ||
                      taskResponse.status === "processing") && (
                      <Progress
                        value={taskResponse.status === "processing" ? 50 : 25}
                        className="w-1/2"
                      />
                    )}
                  </div>
                  {taskResponse.error_message && (
                    <p className="text-sm text-destructive">
                      {taskResponse.error_message}
                    </p>
                  )}
                </div>
              )}
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
