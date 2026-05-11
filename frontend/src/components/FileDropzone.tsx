// FileDropzone.tsx
// A reusable file upload box that supports both drag-and-drop and click-to-browse.
import { useState } from 'react'


// ── Props ─────────────────────────────────────────────────────────────────────

// These are all the values the parent component (App.tsx) passes in.
type Props = {
  label: string                       // e.g. "Resume" or "Job description"
  hint: string                        // e.g. "PDF or DOCX"
  accept: string                      // File types the browser allows e.g. ".pdf,.docx"
  value: File | null                  // The currently selected file (or null if none)
  isBusy: boolean                     // True while the upload/analysis is running
  isAllowedFile: (file: File) => boolean  // Function to check if a file type is valid
  onChange: (file: File | null) => void   // Called when the user picks or clears a file
}


// ── Helper ────────────────────────────────────────────────────────────────────

/**
 * Build the helper text shown below the label.
 * - If a file is selected: show its name.
 * - If no file is selected: show the label + accepted format hint.
 */
function buildHelperText(label: string, hint: string, value: File | null): string {
  if (value) return `${label} selected: ${value.name}`
  return `${label}: ${hint}`
}


// ── Component ─────────────────────────────────────────────────────────────────

export function FileDropzone(props: Props) {
  // Track whether the user is currently dragging a file over this box.
  const [isDragging, setIsDragging] = useState(false)

  // Build the helper text based on current state.
  const helperText = buildHelperText(props.label, props.hint, props.value)

  /**
   * Read the first file from a FileList and pass it to the parent via onChange.
   * We ignore any extra files (only one file per dropzone).
   * If the file type is not allowed, we call onChange(null) to clear the selection.
   */
  function setFromFileList(files: FileList | null) {
    // Get the first file, or null if the list is empty.
    const file = files?.item(0) ?? null

    if (!file) {
      props.onChange(null)
      return
    }

    if (!props.isAllowedFile(file)) {
      // File type is not supported — clear the selection.
      props.onChange(null)
      return
    }

    // File is valid — pass it up to the parent.
    props.onChange(file)
  }


  // ── Drag-and-Drop Event Handlers ──────────────────────────────────────────

  function onDrop(event: React.DragEvent<HTMLDivElement>) {
    // Prevent the browser's default behaviour of opening the file in a new tab.
    event.preventDefault()
    setIsDragging(false)

    // Don't accept drops while the analysis is running.
    if (props.isBusy) return

    setFromFileList(event.dataTransfer.files)
  }


  function onDragOver(event: React.DragEvent<HTMLDivElement>) {
    // We MUST call preventDefault() here, otherwise the onDrop event won't fire.
    event.preventDefault()

    if (props.isBusy) return

    setIsDragging(true)
  }

  function onDragLeave() {
    // User moved the dragged file away from the box — reset the highlight.
    setIsDragging(false)
  }


  // ── Styles ────────────────────────────────────────────────────────────────

  // The drop area changes appearance when the user drags a file over it.
  const dropAreaClasses = [
    'mt-4 rounded-xl border border-dashed p-6 text-sm transition-all duration-200 cursor-pointer',
    isDragging
      ? 'border-violet-400 bg-violet-500/10 scale-[1.01]'   // Highlighted while dragging
      : 'border-zinc-700 hover:border-violet-500 hover:bg-violet-500/5',  // Subtle hover effect
  ].join(' ')

  
  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <section className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-5 transition-all duration-200 hover:border-zinc-700">

      {/* Header row: label on the left, Clear button on the right */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-sm font-semibold">{props.label}</h2>
          <p className="mt-1 text-sm text-zinc-400">{helperText}</p>
        </div>

        {/* Clear button — removes the selected file */}
        <button
          type="button"
          onClick={() => props.onChange(null)}
          disabled={props.isBusy || !props.value}
          className="rounded-lg border border-zinc-700 px-3 py-1 text-xs text-zinc-200
                     transition-all duration-150
                     hover:border-red-500 hover:text-red-400 hover:bg-red-500/10
                     disabled:cursor-not-allowed disabled:opacity-40"
        >
          Clear
        </button>
      </div>

      {/* Drop area — handles both drag-and-drop and click-to-browse */}
      <div
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        className={dropAreaClasses}
      >
        <p className="text-zinc-300">
          Drag and drop here, or{' '}

          {/*
            We wrap the hidden file input in a <label> so clicking the word
            "browse" opens the file picker. The input itself is invisible.
          */}
          <label className="cursor-pointer font-semibold text-violet-300 underline underline-offset-4
                            hover:text-violet-200 transition-colors duration-150">
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

        {/* Show which file types are accepted */}
        <p className="mt-2 text-xs text-zinc-500">Accepted: {props.accept}</p>

        {/* Show a checkmark when a file has been successfully selected */}
        {props.value && (
          <p className="mt-2 text-xs text-violet-400 font-medium">
            ✓ {props.value.name} ready to upload
          </p>
        )}
      </div>
    </section>
  )
}
