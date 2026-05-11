// App.tsx
// This is the main page of the app.
// It manages all state (selected files, loading, errors, results)
// and renders the full UI.
import { useState } from 'react'
import { FileDropzone } from './components/FileDropzone'
import { analyzeResumeAndJob } from './lib/api'
import { formatBytes } from './lib/format'


// ── Constants ─────────────────────────────────────────────────────────────────

// The only file types we accept. The backend also enforces this independently.
const ALLOWED_EXTENSIONS = ['.pdf', '.docx']


// ── Types ─────────────────────────────────────────────────────────────────────

// Tracks which files the user has selected so far.
type UploadState = {
  resumeFile: File | null
  jobFile: File | null
}

// Holds the result returned by the backend after analysis.
type AnalysisState = {
  matchScore: number
  tailoredResume: string
}


// ── Helper Functions ──────────────────────────────────────────────────────────

/**
 * Check whether a file has a supported extension (.pdf or .docx).
 * We lowercase the name first so "Resume.PDF" is treated the same as "resume.pdf".
 * Note: the backend also validates this — this is just a quick frontend check.
 */
function hasAllowedExtension(file: File): boolean {
  const name = file.name.toLowerCase()
  return ALLOWED_EXTENSIONS.some((ext) => name.endsWith(ext))
}

/**
 * Return a message telling the user which files are still missing,
 * or null if both files are selected and we're ready to submit.
 */
function getMissingFilesMessage(upload: UploadState): string | null {
  if (!upload.resumeFile && !upload.jobFile) return 'Upload your resume and the job description.'
  if (!upload.resumeFile) return 'Upload your resume.'
  if (!upload.jobFile) return 'Upload the job description.'
  return null  // Both files are present — ready to go!
}

/**
 * Pick a color for the match score bar based on how high the score is.
 *   0–39  → red    (poor match)
 *   40–69 → yellow (average match)
 *   70–100→ green  (good match)
 */
function getScoreBarColor(score: number): string {
  if (score >= 70) return 'bg-emerald-400'
  if (score >= 40) return 'bg-yellow-400'
  return 'bg-red-400'
}

/**
 * Return a short label describing how good the match is.
 */
function getScoreLabel(score: number): string {
  if (score >= 70) return 'Great match!'
  if (score >= 40) return 'Moderate match'
  return 'Low match'
}


// ── Main Component ────────────────────────────────────────────────────────────

export default function App() {

  // ── State ─────────────────────────────────────────────────────────────────

  // The two uploaded files.
  const [upload, setUpload] = useState<UploadState>({
    resumeFile: null,
    jobFile: null,
  })

  // True while the backend request is in progress.
  const [isLoading, setIsLoading] = useState(false)

  // A short status message shown near the button ("Uploading…", "Done.", etc.)
  const [statusText, setStatusText] = useState<string | null>(null)

  // An error message shown if something goes wrong.
  const [errorText, setErrorText] = useState<string | null>(null)

  // The analysis result from the backend (null until we get a successful response).
  const [analysis, setAnalysis] = useState<AnalysisState | null>(null)


  // ── Derived Values ────────────────────────────────────────────────────────

  // Check which files are missing and build a hint message.
  const missingMessage = getMissingFilesMessage(upload)

  // The submit button is only enabled when both files are selected and we're not loading.
  const canSubmit = !isLoading && missingMessage === null


  // ── Event Handlers ────────────────────────────────────────────────────────

  /**
   * Update just the resumeFile in the upload state, keeping jobFile unchanged.
   *
   * The spread operator `{ ...upload, resumeFile: file }` creates a new object
   * that copies all existing fields from `upload` and then overrides `resumeFile`.
   * This is how you update one field of a state object in React.
   */
  function handleResumeChange(file: File | null) {
    setUpload({ ...upload, resumeFile: file })
  }

  function handleJobChange(file: File | null) {
    setUpload({ ...upload, jobFile: file })
  }

  /**
   * Send both files to the backend and handle the response.
   *
   * Uses async/await so the code reads top-to-bottom without nested callbacks.
   * The try/catch block handles any errors that occur during the request.
   */
  async function handleSubmit() {
    // Guard: don't run if the button should be disabled.
    if (!canSubmit || !upload.resumeFile || !upload.jobFile) return

    // Reset previous results and errors before starting a new request.
    setErrorText(null)
    setAnalysis(null)
    setIsLoading(true)
    setStatusText('Uploading…')

    try {
      // Send the files to the backend and wait for the result.
      const result = await analyzeResumeAndJob(upload.resumeFile, upload.jobFile)

      // Store the result — this will make the Results section appear below.
      setAnalysis({
        matchScore: result.match_score,
        tailoredResume: result.tailored_resume,
      })

      setStatusText('Done.')

    } catch (err) {
      // If anything went wrong, show the error message to the user.
      // `err instanceof Error` checks if it's a proper Error object with a `.message`.
      setErrorText(err instanceof Error ? err.message : String(err))
      setStatusText(null)

    } finally {
      // This runs whether the request succeeded or failed.
      setIsLoading(false)
    }
  }

  
  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="mx-auto w-full max-w-5xl px-4 py-10">

        {/* ── Page Header ── */}
        <header className="mb-8">
          <p className="text-sm text-violet-400 font-medium tracking-wide uppercase">AI Resume Polisher</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">
            Upload your resume and job description
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-zinc-400">
            We'll compare your resume to the job posting and generate a tailored version. Supported formats: PDF and DOCX.
          </p>
        </header>

        {/* ── File Upload Section ── */}
        {/* Two dropzones side by side on medium+ screens, stacked on mobile */}
        <div className="grid gap-6 md:grid-cols-2">
          <FileDropzone
            label="Resume"
            hint="PDF or DOCX"
            value={upload.resumeFile}
            accept={ALLOWED_EXTENSIONS.join(',')}
            isBusy={isLoading}
            isAllowedFile={hasAllowedExtension}
            onChange={handleResumeChange}
          />
          <FileDropzone
            label="Job description"
            hint="PDF or DOCX"
            value={upload.jobFile}
            accept={ALLOWED_EXTENSIONS.join(',')}
            isBusy={isLoading}
            isAllowedFile={hasAllowedExtension}
            onChange={handleJobChange}
          />
        </div>

        {/* ── Summary & Submit ── */}
        <div className="mt-6 rounded-2xl border border-zinc-800 bg-zinc-900/50 p-5 transition-all duration-200">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

            {/* File summary */}
            <div>
              <p className="text-sm font-medium">Summary</p>
              <p className="mt-1 text-sm text-zinc-400">
                {upload.resumeFile
                  ? `Resume: ${upload.resumeFile.name} (${formatBytes(upload.resumeFile.size)})`
                  : 'Resume: —'}
                <br />
                {upload.jobFile
                  ? `Job: ${upload.jobFile.name} (${formatBytes(upload.jobFile.size)})`
                  : 'Job: —'}
              </p>
            </div>

            {/* Submit button */}
            <button
              type="button"
              onClick={handleSubmit}
              disabled={!canSubmit}
              className="inline-flex items-center justify-center rounded-xl
                         bg-violet-500 px-5 py-2.5 text-sm font-semibold text-zinc-950
                         shadow-sm transition-all duration-150
                         hover:bg-violet-400 hover:scale-[1.03] hover:shadow-violet-500/30 hover:shadow-md
                         active:scale-[0.98]
                         disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:scale-100 disabled:hover:shadow-none"
            >
              {isLoading ? 'Analysing…' : 'Analyse →'}
            </button>
          </div>

          {/* Hint shown when files are missing */}
          {missingMessage && (
            <p className="mt-3 text-sm text-zinc-400">{missingMessage}</p>
          )}

          {/* Status message (e.g. "Uploading…" or "Done.") */}
          {statusText && (
            <p className="mt-3 text-sm text-violet-300 animate-pulse">{statusText}</p>
          )}

          {/* Error message shown in a red box */}
          {errorText && (
            <p className="mt-3 whitespace-pre-wrap rounded-xl border border-red-900/60 bg-red-950/30 p-3 text-sm text-red-200">
              ⚠ {errorText}
            </p>
          )}
        </div>

        {/* ── Results Section ── */}
        {/* Only shown after a successful analysis */}
        {analysis && (
          <section className="mt-6 rounded-2xl border border-zinc-800 bg-zinc-900/50 p-5 transition-all duration-500">
            <h2 className="text-sm font-semibold text-zinc-100">Results</h2>

            {/* Match score bar */}
            <div className="mt-4">
              <div className="flex items-center justify-between text-sm mb-1">
                <p className="text-zinc-300">Match score</p>
                <div className="flex items-center gap-2">
                  {/* Label like "Great match!" */}
                  <span className="text-xs text-zinc-400">{getScoreLabel(analysis.matchScore)}</span>
                  {/* The score number */}
                  <p className="font-semibold text-zinc-100">{analysis.matchScore}%</p>
                </div>
              </div>

              {/* Progress bar — width is set dynamically based on the score */}
              <div className="h-2.5 w-full overflow-hidden rounded-full bg-zinc-800">
                <div
                  className={`h-full rounded-full transition-[width] duration-700 ${getScoreBarColor(analysis.matchScore)}`}
                  style={{ width: `${analysis.matchScore}%` }}
                />
              </div>
            </div>

            {/* Tailored resume text */}
            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-zinc-300 font-medium">Tailored resume</p>
                {/* Copy to clipboard button */}
                <button
                  type="button"
                  onClick={() => navigator.clipboard.writeText(analysis.tailoredResume)}
                  className="rounded-lg border border-zinc-700 px-3 py-1 text-xs text-zinc-300
                             transition-all duration-150
                             hover:border-violet-500 hover:text-violet-300 hover:bg-violet-500/10"
                >
                  Copy
                </button>
              </div>

              {/* Scrollable preformatted text block */}
              <pre className="max-h-[520px] overflow-auto rounded-xl border border-zinc-800
                              bg-zinc-950/60 p-4 text-sm leading-6 text-zinc-100
                              whitespace-pre-wrap">
                {analysis.tailoredResume}
              </pre>
            </div>
          </section>
        )}

      </div>
    </div>
  )
}
