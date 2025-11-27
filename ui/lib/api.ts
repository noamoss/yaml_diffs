/** API client for Railway backend. */

import { DiffRequest, DiffResponse, ErrorResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Test API connectivity (for debugging)
 */
export async function testApiConnection(): Promise<{ success: boolean; message: string }> {
  try {
    // Try root endpoint first, then health
    const testUrls = [`${API_URL}/`, `${API_URL}/health`];

    let response: Response | null = null;
    let lastError: Error | null = null;

    // Try each URL
    for (const testUrl of testUrls) {
      try {
        response = await fetch(testUrl, {
          method: "GET",
          mode: "cors",
          headers: {
            "Accept": "application/json",
          },
        });
        if (response.ok || response.status !== 404) {
          break; // Found a working endpoint
        }
      } catch (err) {
        lastError = err instanceof Error ? err : new Error(String(err));
        continue;
      }
    }

    if (!response) {
      throw lastError || new Error("Failed to connect to any endpoint");
    }


    if (response.status === 404) {
      return {
        success: false,
        message: `❌ Service Not Found (404): The Railway service at ${API_URL} appears to be down or not deployed. Check Railway dashboard to ensure the service is running.`
      };
    }

    if (response.ok) {
      try {
        const data = await response.json();
        return { success: true, message: `✅ API is reachable! Status: ${data.status || 'OK'}, Version: ${data.version || 'unknown'}` };
      } catch {
        return { success: true, message: `✅ API is reachable! Status: ${response.status}` };
      }
    } else {
      return { success: false, message: `❌ API returned status ${response.status}: ${response.statusText}` };
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);

    // Check for CORS-specific errors
    if (errorMsg.includes("CORS") || errorMsg.includes("Failed to fetch")) {
      return {
        success: false,
        message: `❌ CORS Error: The Railway API is blocking requests from ${typeof window !== 'undefined' ? window.location.origin : 'localhost:3000'}. Add "http://localhost:3000" to the CORS_ORIGINS environment variable in Railway project settings.`
      };
    }

    return {
      success: false,
      message: `❌ Failed to connect: ${errorMsg}. Check your network connection and Railway API status.`
    };
  }
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: Array<Record<string, unknown>> | null
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Enhance validation error messages with helpful guidance
 */
function enhanceValidationErrorMessage(
  baseMessage: string,
  details: Array<Record<string, unknown>>
): string {
  let enhanced = baseMessage;
  const hints: string[] = [];

  // Check for version field errors
  const versionError = details.find(
    (d) =>
      typeof d.loc === "object" &&
      d.loc !== null &&
      Array.isArray(d.loc) &&
      d.loc.includes("version")
  );
  if (versionError) {
    hints.push(
      `\n\n💡 The 'version' field must be an object with a 'number' field:\n` +
        `   version:\n` +
        `     number: "1.0"  # or "2024-01-01", "v2.0", etc.\n` +
        `     description: "Optional description"  # optional`
    );
  }

  // Check for source field errors
  const sourceError = details.find(
    (d) =>
      typeof d.loc === "object" &&
      d.loc !== null &&
      Array.isArray(d.loc) &&
      d.loc.includes("source")
  );
  if (sourceError) {
    hints.push(
      `\n\n💡 The 'source' field must be an object with 'url' and 'fetched_at' fields:\n` +
        `   source:\n` +
        `     url: "https://example.com/document"  # Must be a valid URI\n` +
        `     fetched_at: "2025-01-20T09:50:00Z"  # ISO 8601 format`
    );
  }

  if (hints.length > 0) {
    enhanced = baseMessage + "\n" + hints.join("\n");
  }

  return enhanced;
}

export async function diffDocuments(
  oldYaml: string,
  newYaml: string
): Promise<DiffResponse> {
  const request: DiffRequest = {
    old_yaml: oldYaml,
    new_yaml: newYaml,
  };

  const requestUrl = `${API_URL}/api/v1/diff`;
  const requestBody = JSON.stringify(request);

  try {
    const response = await fetch(requestUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: requestBody,
      mode: "cors", // Explicitly set CORS mode
    });

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      let errorDetails: Array<Record<string, unknown>> | null = null;

      try {
        const errorData: ErrorResponse = await response.json();
        errorMessage = errorData.message || errorMessage;
        errorDetails = errorData.details || null;

        // Enhance error message with helpful guidance for common validation errors
        if (errorDetails && Array.isArray(errorDetails)) {
          const enhancedMessage = enhanceValidationErrorMessage(errorMessage, errorDetails);
          if (enhancedMessage !== errorMessage) {
            errorMessage = enhancedMessage;
          }
        }

      } catch (parseError) {
        // If JSON parsing fails, use status text
        if (process.env.NODE_ENV === 'development') {
          console.warn('Failed to parse error response as JSON:', parseError);
        }
        errorMessage = response.statusText || errorMessage;
      }

      throw new ApiError(errorMessage, response.status, errorDetails);
    }

    const data: DiffResponse = await response.json();

    // Ensure all changes have an id field (fallback for older API versions)
    if (data.diff?.changes) {
      data.diff.changes = data.diff.changes.map((change, index) => {
        if (!change.id) {
          // Generate a fallback ID based on change properties
          const fallbackId = `${change.section_id}-${change.change_type}-${change.marker}-${index}`;
          if (process.env.NODE_ENV === 'development') {
            console.warn(`Change missing id field, using fallback ID: ${fallbackId}`);
          }
          return { ...change, id: fallbackId };
        }
        return change;
      });
    }

    return data;
  } catch (error) {

    if (error instanceof ApiError) {
      throw error;
    }
    // Network or other errors
    let errorMessage = error instanceof Error ? error.message : "Network error occurred";

    // Provide more helpful error messages
    if (errorMessage === "Failed to fetch" || errorMessage.includes("fetch")) {
      if (API_URL.includes("localhost:8000")) {
        errorMessage = `Failed to connect to API at ${API_URL}. Make sure the API server is running locally, or set NEXT_PUBLIC_API_URL environment variable to your Railway API URL.`;
      } else {
        // Most likely CORS issue when connecting to Railway from localhost
        errorMessage = `CORS Error: Railway API is blocking requests from http://localhost:3000. If you've already added it to CORS_ORIGINS, Railway may need to redeploy. Try: 1) Wait 2-3 minutes for auto-redeploy, or 2) Go to Railway dashboard → Your service → Settings → Redeploy, or 3) Make a small change to trigger redeploy.`;
      }
    }

    throw new ApiError(errorMessage, 0);
  }
}
