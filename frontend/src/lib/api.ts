type AnalysisResponse = {
  match_score: number
  tailored_resume: string
}

const DEFAULT_API_BASE_URL = 'http://127.0.0.1:5000'

function getApiBaseUrl(): string {
  // Lets us change the backend URL with an env var later.
  const envUrl = import.meta.env.VITE_API_BASE_URL as string | undefined
  if (!envUrl) return DEFAULT_API_BASE_URL
  return envUrl
}

function buildAnalyzeUrl(): string {
  // Keeping this in one function makes future changes easier.
  return `${getApiBaseUrl()}/analyze`
}

function toErrorMessage(value: unknown): string {
  // Fetch errors can be anything; always show a readable string.
  if (value instanceof Error) return value.message
  return String(value)
}

async function readTextSafely(response: Response): Promise<string> {
  // Backend sends plain text errors sometimes, so we read text first.
  try {
    return await response.text()
  } catch {
    return ''
  }
}

function validateAnalysisShape(raw: unknown): AnalysisResponse {
  // Frontend should not trust network data. Keep checks simple but strict.
  if (!raw || typeof raw !== 'object') throw new Error('Invalid response: not an object')
  const data = raw as Record<string, unknown>
  if (typeof data.match_score !== 'number') throw new Error('Invalid response: match_score missing')
  if (typeof data.tailored_resume !== 'string') throw new Error('Invalid response: tailored_resume missing')
  return { match_score: data.match_score, tailored_resume: data.tailored_resume }
}

export async function analyzeResumeAndJob(resumeFile: File, jobFile: File): Promise<AnalysisResponse> {
  // Backend expects multipart fields `resume` and `job`.
  const form = new FormData()
  form.append('resume', resumeFile)
  form.append('job', jobFile)

  const response = await fetch(buildAnalyzeUrl(), { method: 'POST', body: form })
  if (!response.ok) {
    const message = await readTextSafely(response)
    throw new Error(message || `Request failed: ${response.status}`)
  }

  try {
    const json = (await response.json()) as unknown
    return validateAnalysisShape(json)
  } catch (err) {
    throw new Error(`Failed to parse JSON: ${toErrorMessage(err)}`)
  }
}

