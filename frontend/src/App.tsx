import { useMemo, useState } from 'react'

import { FileDropzone } from './components/FileDropzone'
import { analyzeResumeAndJob } from './lib/api'
import { formatBytes } from './lib/format'

const ALLOWED_EXTENSIONS = ['.pdf', '.docx']

type UploadState = {
  resumeFile: File | null
  jobFile: File | null
}

type AnalysisState = {
  matchScore: number
  tailoredResume: string
}

function hasAllowedExtension(file: File): boolean {
  // Keep this check simple; the backend still validates.
  const name = file.name.toLowerCase()
  return ALLOWED_EXTENSIONS.some((ext) => name.endsWith(ext))
}

function buildMissingFilesMessage(state: UploadState): string | null {
  // This keeps the button disabled reason consistent with the UI.
  if (!state.resumeFile && !state.jobFile) return 'Upload your resume and the job description.'
  if (!state.resumeFile) return 'Upload your resume.'
  if (!state.jobFile) return 'Upload the job description.'
  return null
}

export default function App() {
  const [upload, setUpload] = useState<UploadState>({ resumeFile: null, jobFile: null })
  const [isLoading, setIsLoading] = useState(false)
  const [statusText, setStatusText] = useState<string | null>(null)
  const [errorText, setErrorText] = useState<string | null>(null)
  const [analysis, setAnalysis] = useState<AnalysisState | null>(null)

  const missingMessage = useMemo(() => buildMissingFilesMessage(upload), [upload])
  const canSubmit = !isLoading && missingMessage === null

  const handleResume = (file: File | null) => setUpload((s) => ({ ...s, resumeFile: file }))
  const handleJob = (file: File | null) => setUpload((s) => ({ ...s, jobFile: file }))

  const handleSubmit = async () => {
    if (!canSubmit || !upload.resumeFile || !upload.jobFile) return
    setErrorText(null)
    setAnalysis(null)
    setIsLoading(true)
    setStatusText('Uploading…')
    try {
      const result = await analyzeResumeAndJob(upload.resumeFile, upload.jobFile)
      setAnalysis({ matchScore: result.match_score, tailoredResume: result.tailored_resume })
      setStatusText('Done.')
    } catch (err) {
      // Keep the error readable; the backend returns plain text on failures.
      setErrorText(err instanceof Error ? err.message : String(err))
      setStatusText(null)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="mx-auto w-full max-w-5xl px-4 py-10">
        <header className="mb-8">
          <p className="text-sm text-zinc-400">AI Resume Polisher</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">
            Upload your resume and job description
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-zinc-300">
            Supported formats: PDF and DOCX.
          </p>
        </header>

        <div className="grid gap-6 md:grid-cols-2">
          <FileDropzone
            label="Resume"
            hint="PDF or DOCX"
            value={upload.resumeFile}
            accept={ALLOWED_EXTENSIONS.join(',')}
            isBusy={isLoading}
            isAllowedFile={hasAllowedExtension}
            onChange={handleResume}
          />
          <FileDropzone
            label="Job description"
            hint="PDF or DOCX"
            value={upload.jobFile}
            accept={ALLOWED_EXTENSIONS.join(',')}
            isBusy={isLoading}
            isAllowedFile={hasAllowedExtension}
            onChange={handleJob}
          />
        </div>

        <div className="mt-6 rounded-2xl border border-zinc-800 bg-zinc-900/50 p-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-medium">Summary</p>
              <p className="mt-1 text-sm text-zinc-400">
                {upload.resumeFile ? `Resume: ${upload.resumeFile.name} (${formatBytes(upload.resumeFile.size)})` : 'Resume: —'}
                <br />
                {upload.jobFile ? `Job: ${upload.jobFile.name} (${formatBytes(upload.jobFile.size)})` : 'Job: —'}
              </p>
            </div>

            <button
              type="button"
              onClick={handleSubmit}
              disabled={!canSubmit}
              className="inline-flex items-center justify-center rounded-xl bg-violet-500 px-4 py-2 text-sm font-semibold text-zinc-950 shadow-sm transition disabled:cursor-not-allowed disabled:opacity-40"
            >
              {isLoading ? 'Loading…' : 'Continue'}
            </button>
          </div>

          {missingMessage ? (
            <p className="mt-3 text-sm text-zinc-400">{missingMessage}</p>
          ) : null}
          {statusText ? <p className="mt-3 text-sm text-zinc-300">{statusText}</p> : null}
          {errorText ? (
            <p className="mt-3 whitespace-pre-wrap rounded-xl border border-red-900/60 bg-red-950/30 p-3 text-sm text-red-200">
              {errorText}
            </p>
          ) : null}
        </div>

        {analysis ? (
          <section className="mt-6 rounded-2xl border border-zinc-800 bg-zinc-900/50 p-5">
            <h2 className="text-sm font-semibold">Results</h2>

            <div className="mt-3">
              <div className="flex items-center justify-between text-sm">
                <p className="text-zinc-300">Match score</p>
                <p className="font-semibold text-zinc-100">{analysis.matchScore}%</p>
              </div>
              <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-zinc-800">
                <div
                  className="h-full rounded-full bg-violet-400 transition-[width] duration-700"
                  style={{ width: `${analysis.matchScore}%` }}
                />
              </div>
            </div>

            <div className="mt-5">
              <p className="text-sm text-zinc-300">Tailored resume</p>
              <pre className="mt-2 max-h-[520px] overflow-auto rounded-xl border border-zinc-800 bg-zinc-950/40 p-4 text-sm leading-6 text-zinc-100">
                {analysis.tailoredResume}
              </pre>
            </div>
          </section>
        ) : null}
      </div>
    </div>
  )
}
