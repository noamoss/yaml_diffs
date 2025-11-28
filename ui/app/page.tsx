"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import YamlEditor from "@/components/YamlEditor";
import FileUpload from "@/components/FileUpload";
import DiffView from "@/components/DiffView";
import ExportButton from "@/components/ExportButton";
import { diffDocuments, ApiError, testApiConnection } from "@/lib/api";
import { DocumentDiff } from "@/lib/types";

type ViewMode = "editor" | "diff";

export default function Home() {
  const [oldYaml, setOldYaml] = useState("");
  const [newYaml, setNewYaml] = useState("");
  const [viewMode, setViewMode] = useState<ViewMode>("editor");
  const [diff, setDiff] = useState<DocumentDiff | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [apiTestResult, setApiTestResult] = useState<string | null>(null);

  const diffMutation = useMutation({
    mutationFn: ({ oldYaml, newYaml }: { oldYaml: string; newYaml: string }) =>
      diffDocuments(oldYaml, newYaml),
    onSuccess: (data) => {
      setDiff(data.diff);
      setViewMode("diff");
      setError(null);
    },
    onError: (err: unknown) => {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred");
      }
      setDiff(null);
    },
  });

  const handleTestApi = async () => {
    setApiTestResult("Testing API connection...");
    const result = await testApiConnection();
    setApiTestResult(result.message);
  };

  const handleRunDiff = () => {
    if (!oldYaml.trim() || !newYaml.trim()) {
      setError("Please provide both old and new YAML content");
      return;
    }

    // Basic validation - check if YAML contains 'document:' key
    // Allow whitespace/comments before document: key
    const oldYamlTrimmed = oldYaml.trim();
    const newYamlTrimmed = newYaml.trim();
    const documentKeyPattern = /^#.*\n?document:|^document:/m;

    if (!documentKeyPattern.test(oldYamlTrimmed)) {
      setError("YAML must have 'document:' as the top-level key. Example:\n\ndocument:\n  id: \"test\"\n  title: \"Test\"\n  ...");
      return;
    }
    if (!documentKeyPattern.test(newYamlTrimmed)) {
      setError("YAML must have 'document:' as the top-level key. Example:\n\ndocument:\n  id: \"test\"\n  title: \"Test\"\n  ...");
      return;
    }

    setError(null);
    diffMutation.mutate({ oldYaml, newYaml });
  };

  const handleOldYamlLoad = (content: string) => {
    setOldYaml(content);
    setError(null);
  };

  const handleNewYamlLoad = (content: string) => {
    setNewYaml(content);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between h-auto sm:h-16 py-3 sm:py-0 gap-3 sm:gap-0">
            <h1 className="text-xl font-semibold text-gray-900">
              YAML Diff Viewer
            </h1>
            <div className="flex items-center gap-2 sm:gap-3 w-full sm:w-auto">
              <button
                onClick={handleTestApi}
                className="px-3 sm:px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors text-sm sm:text-base"
                title="Test API connection"
              >
                Test API
              </button>
              <ExportButton diff={diff} disabled={!diff} />
              <button
                onClick={handleRunDiff}
                disabled={diffMutation.isPending || !oldYaml.trim() || !newYaml.trim()}
                className="px-3 sm:px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors text-sm sm:text-base flex-1 sm:flex-initial"
              >
                {diffMutation.isPending ? (
                  <span className="flex items-center gap-2 justify-center">
                    <svg
                      className="animate-spin h-4 w-4"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    <span className="hidden sm:inline">Running...</span>
                    <span className="sm:hidden">...</span>
                  </span>
                ) : (
                  "Run Diff"
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="border-b border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            <button
              onClick={() => setViewMode("editor")}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                viewMode === "editor"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              Editor
            </button>
            <button
              onClick={() => setViewMode("diff")}
              disabled={!diff}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                viewMode === "diff"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
              }`}
            >
              Diff View
            </button>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {apiTestResult && (
          <div className={`mb-4 border rounded-lg p-4 ${
            apiTestResult.includes("reachable") || apiTestResult.includes("OK")
              ? "bg-green-50 border-green-200"
              : "bg-yellow-50 border-yellow-200"
          }`}>
            <div className="flex items-start">
              <div className="flex-shrink-0">
                {apiTestResult.includes("reachable") || apiTestResult.includes("OK") ? (
                  <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
              <div className="ml-3">
                <h3 className={`text-sm font-medium ${
                  apiTestResult.includes("reachable") || apiTestResult.includes("OK")
                    ? "text-green-800"
                    : "text-yellow-800"
                }`}>
                  API Connection Test
                </h3>
                <div className={`mt-2 text-sm ${
                  apiTestResult.includes("reachable") || apiTestResult.includes("OK")
                    ? "text-green-700"
                    : "text-yellow-700"
                }`}>
                  <p>{apiTestResult}</p>
                </div>
              </div>
            </div>
          </div>
        )}
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-red-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3 flex-1">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">
                  <pre className="whitespace-pre-wrap font-sans">{error}</pre>
                </div>
              </div>
            </div>
          </div>
        )}

        {viewMode === "editor" ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
              <div className="space-y-4">
                <FileUpload
                  onFileLoad={handleOldYamlLoad}
                  label="Old Version"
                />
                <div className="h-[400px] sm:h-[500px]">
                  <YamlEditor
                    value={oldYaml}
                    onChange={setOldYaml}
                    placeholder="Paste or type old YAML version here..."
                  />
                </div>
              </div>
              <div className="space-y-4">
                <FileUpload
                  onFileLoad={handleNewYamlLoad}
                  label="New Version"
                />
                <div className="h-[400px] sm:h-[500px]">
                  <YamlEditor
                    value={newYaml}
                    onChange={setNewYaml}
                    placeholder="Paste or type new YAML version here..."
                  />
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div>
            {diff ? (
              <DiffView diff={diff} oldYaml={oldYaml} newYaml={newYaml} />
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-500">
                  Run a diff to see changes here.
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
