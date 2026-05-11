const BYTES_IN_KB = 1024
const BYTES_IN_MB = BYTES_IN_KB * 1024

export function formatBytes(byteCount: number): string {
  // Small helper so components don’t repeat the same formatting code.
  if (byteCount < BYTES_IN_KB) return `${byteCount} B`
  if (byteCount < BYTES_IN_MB) return `${(byteCount / BYTES_IN_KB).toFixed(1)} KB`
  return `${(byteCount / BYTES_IN_MB).toFixed(1)} MB`
}

