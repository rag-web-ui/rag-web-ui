"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";
import { api, ApiError } from "@/lib/api";
import DashboardLayout from "@/components/layout/dashboard-layout";
import { Search, ArrowRight, Sparkles } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface KnowledgeBase {
  id: number;
  name: string;
  description: string;
}

export default function TestPage({ params }: { params: { id: string } }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBase | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [topK, setTopK] = useState("3");
  const { toast } = useToast();

  useEffect(() => {
    const fetchKnowledgeBase = async () => {
      try {
        const data = await api.get(
          `http://localhost:8000/api/knowledge-base/${params.id}`
        );
        setKnowledgeBase(data);
      } catch (error) {
        console.error("Failed to fetch knowledge base:", error);
        if (error instanceof ApiError) {
          toast({
            title: "Error",
            description: error.message,
            variant: "destructive",
          });
        }
      }
    };

    fetchKnowledgeBase();
  }, [params.id]);

  const handleTest = async () => {
    if (!query) {
      toast({
        title: "Please fill in all fields",
        description: "Please enter query text",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const data = await api.post(
        "http://localhost:8000/api/knowledge-base/test-retrieval",
        {
          query,
          kb_id: parseInt(params.id),
          top_k: parseInt(topK),
        }
      );

      setResults(data.results);
    } catch (error) {
      toast({
        title: "测试失败",
        description: error instanceof Error ? error.message : "未知错误",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (!knowledgeBase) {
    return null;
  }

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-gradient-to-b from-background to-background/50">
        <div className="max-w-6xl mx-auto py-12 px-6">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/60">
              知识库检索测试
            </h1>
            <p className="mt-4 text-lg text-muted-foreground">
              <span className="font-semibold text-foreground">
                {knowledgeBase.name}
              </span>
              {knowledgeBase.description && <span className="mx-2">•</span>}
              <span className="italic">{knowledgeBase.description}</span>
            </p>
          </div>

          <Card className="backdrop-blur-sm bg-card/50 border-primary/20">
            <CardContent className="p-8">
              <div className="flex gap-4">
                <div className="relative flex-1">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <Input
                    placeholder="输入您想要查询的内容..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="pl-12 h-14 text-lg bg-background/50 border-primary/20 focus:border-primary"
                    onKeyDown={(e) => e.key === "Enter" && handleTest()}
                    disabled={loading}
                  />
                  <Button
                    onClick={handleTest}
                    size="lg"
                    className="absolute right-0 top-0 h-14 px-8 bg-primary hover:bg-primary/90"
                    disabled={loading}
                  >
                    {loading ? (
                      <span className="flex items-center">
                        <Sparkles className="animate-spin mr-2 h-4 w-4" />
                        搜索中...
                      </span>
                    ) : (
                      <span className="flex items-center">
                        搜索
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </span>
                    )}
                  </Button>
                </div>

                <Select value={topK} onValueChange={setTopK}>
                  <SelectTrigger className="w-[140px] h-14 bg-background/50 border-primary/20">
                    <SelectValue placeholder="返回数量" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Top 1</SelectItem>
                    <SelectItem value="3">Top 3</SelectItem>
                    <SelectItem value="5">Top 5</SelectItem>
                    <SelectItem value="10">Top 10</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {results.length > 0 && (
            <div className="mt-12 space-y-8">
              <h2 className="text-2xl font-semibold flex items-center gap-2">
                <Sparkles className="h-6 w-6 text-primary" />
                搜索结果
              </h2>
              <div className="grid gap-6">
                {results.map((result, index) => (
                  <Card
                    key={index}
                    className="overflow-hidden border-0 shadow-lg hover:shadow-xl transition-shadow duration-300 bg-card/50 backdrop-blur-sm"
                  >
                    <CardContent className="p-8">
                      <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-4">
                          <span className="px-4 py-2 rounded-full bg-primary/10 text-primary font-medium">
                            相关度: {(result.score * 100).toFixed(2)}%
                          </span>
                          <span className="text-sm text-muted-foreground flex items-center gap-2">
                            <Search className="h-4 w-4" />
                            来源: {result.metadata.source}
                          </span>
                        </div>
                      </div>
                      <p className="text-lg leading-relaxed whitespace-pre-wrap prose prose-gray max-w-none">
                        {result.content}
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
