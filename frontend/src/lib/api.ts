// api.ts
// This file handles all communication between the frontend and the backend.
// It sends uploaded files to the backend and returns the AI analysis result.


// ── Types ─────────────────────────────────────────────────────────────────────

// This describes the shape of the JSON the backend sends back on success.
type AnalysisResponse = {
  match_score: number       // A number from 0 to 100
  tailored_resume: string   // The rewritten resume text
}


// ── Configuration ─────────────────────────────────────────────────────────────

// Default backend URL used during local development.
const DEFAULT_API_BASE_URL = 'http://127.0.0.1:5000'

/**
 * Get the backend base URL.
 *
 * During development this returns DEFAULT_API_BASE_URL.
 * In production you can set VITE_API_BASE_URL in a .env file to override it.
 * Example .env line: VITE_API_BASE_URL=https://mybackend.com
 */
function getApiBaseUrl(): string {
  const envUrl = import.meta.env.VITE_API_BASE_URL as string | undefined
  if (!envUrl) return DEFAULT_API_BASE_URL
  return envUrl
}

/**
 * Build the full URL for the /analyze endpoint.
 * Example: "http://127.0.0.1:5000/analyze"
 */
function buildAnalyzeUrl(): string {
  return `${getApiBaseUrl()}/analyze`
}


// ── Error Handling Helpers ────────────────────────────────────────────────────

/**
 * Convert any thrown value into a readable string.
 *
 * When we use try/catch, the caught value might be an Error object or
 * something else entirely. This always gives us a string we can show the user.
 */
function toErrorMessage(value: unknown): string {
  if (value instanceof Error) return value.message
  return String(value)
}

/**
 * Safely read the response body as plain text.
 *
 * The backend sends plain text error messages (not JSON) when something goes wrong,
 * so we always try to read the body as text first.
 */
async function readTextSafely(response: Response): Promise<string> {
  try {
    return await response.text()
  } catch {
    // If reading the body fails for any reason, return an empty string.
    return ''
  }
}


// ── Response Validation ───────────────────────────────────────────────────────

/**
 * Check that the data from the backend has the fields we expect.
 *
 * We never fully trust data coming from the network, so we verify
 * that `match_score` is a number and `tailored_resume` is a string
 * before using them in the UI.
 */
function validateAnalysisShape(raw: unknown): AnalysisResponse {
  // The response must be an object (not null, not an array, not a string).
  if (!raw || typeof raw !== 'object') {
    throw new Error('Invalid response: not an object')
  }

  // Cast to a generic object so we can check individual keys.
  const data = raw as Record<string, unknown>

  if (typeof data.match_score !== 'number') {
    throw new Error('Invalid response: match_score missing or wrong type')
  }

  if (typeof data.tailored_resume !== 'string') {
    throw new Error('Invalid response: tailored_resume missing or wrong type')
  }

  return {
    match_score: data.match_score,
    tailored_resume: data.tailored_resume,
  }
}


// ── Main API Function ─────────────────────────────────────────────────────────

/**
 * Send the resume and job description files to the backend and return the analysis.
 *
 * Steps:
 * 1. Build a FormData object with both files attached.
 * 2. POST it to the /analyze endpoint.
 * 3. If the response is not OK, throw an error with the backend's message.
 * 4. Parse the JSON response and validate its shape.
 * 5. Return the validated result.
 *
 * Throws an Error if anything goes wrong — the caller (App.tsx) handles it.
 */
export async function analyzeResumeAndJob(
  resumeFile: File,
  jobFile: File,
): Promise<AnalysisResponse> {
  // FormData is the standard way to send files via HTTP.
  // The field names 'resume' and 'job' must match what the backend expects.
  const form = new FormData()
  form.append('resume', resumeFile)
  form.append('job', jobFile)

  // Send the POST request to the backend.
  const response = await fetch(buildAnalyzeUrl(), {
    method: 'POST',
    body: form,
  })

  // If the backend returned an error status (4xx or 5xx), read the message and throw.
  if (!response.ok) {
    const errorMessage = await readTextSafely(response)
    throw new Error(errorMessage || `Request failed with status ${response.status}`)
  }

  // Parse the successful JSON response and validate its shape before returning.
  try {
    const json = await response.json()
    return validateAnalysisShape(json)
  } catch (err) {
    throw new Error(`Failed to parse response from server: ${toErrorMessage(err)}`)
  }
}
