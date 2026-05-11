import { useMemo, useState } from 'react'

type Props = {
  label: string
  hint: string
  accept: string
  value: File | null
  isBusy: boolean
  isAllowedFile: (file: File) => boolean
  onChange: (file: File | null) => void
}

function buildHelperText(label: string, hint: string, value: File | null): string {
  // Keeps the UI text consistent in one place.
  if (value) return `${label} selected: ${value.name}`
  return `${label}: ${hint}`
}

export function FileDropzone(props: Props) {
  const [isDragging, setIsDragging] = useState(false)
  const helperText = useMemo(
    () => buildHelperText(props.label, props.hint, props.value),
    [props.hint, props.label, props.value],
  )

  const setFromFileList = (files: FileList | null) => {
    // Only one file per input keeps the UI simple.
    const candidate = files?.item(0) ?? null
    if (!candidate) return props.onChange(null)
    if (!props.isAllowedFile(candidate)) return props.onChange(null)
    props.onChange(candidate)
  }

  const onDrop = (event: React.DragEvent<HTMLDivElement>) => {
    // Prevent the browser from opening the file.
    event.preventDefault()
    setIsDragging(false)
    if (props.isBusy) return
    setFromFileList(event.dataTransfer.files)
  }

  const onDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    // Required for drop events to work.
    event.preventDefault()
    if (props.isBusy) return
    setIsDragging(true)
  }

  const onDragLeave = () => setIsDragging(false)

  return (
    <section className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-sm font-semibold">{props.label}</h2>
          <p className="mt-1 text-sm text-zinc-400">{helperText}</p>
        </div>
        <button
          type="button"
          onClick={() => props.onChange(null)}
          disabled={props.isBusy || !props.value}
          className="rounded-lg border border-zinc-700 px-3 py-1 text-xs text-zinc-200 transition disabled:cursor-not-allowed disabled:opacity-40"
        >
          Clear
        </button>
      </div>

      <div
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        className={[
          'mt-4 rounded-xl border border-dashed p-5 text-sm transition',
          isDragging ? 'border-violet-400 bg-violet-500/10' : 'border-zinc-700',
        ].join(' ')}
      >
        <p className="text-zinc-300">
          Drag and drop here, or{' '}
          <label className="cursor-pointer font-semibold text-violet-300 underline underline-offset-4">
            browse
            <input
              type="file"
              accept={props.accept}
              disabled={props.isBusy}
              className="hidden"
              onChange={(e) => setFromFileList(e.target.files)}
            />
          </label>
          .
        </p>
        <p className="mt-2 text-xs text-zinc-500">Accepted: {props.accept}</p>
      </div>
    </section>
  )
}

