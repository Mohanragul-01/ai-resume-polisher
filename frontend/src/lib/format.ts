// format.ts
// Helper functions for displaying values in a human-readable way.

// How many bytes are in a kilobyte and a megabyte.
// We define these as named constants so the math below is easy to read.
const BYTES_IN_KB = 1024
const BYTES_IN_MB = BYTES_IN_KB * 1024   // = 1,048,576 bytes

/**
 * Convert a raw byte count into a readable string like "2.3 KB" or "1.1 MB".
 *
 * Examples:
 *   formatBytes(500)        → "500 B"
 *   formatBytes(2048)       → "2.0 KB"
 *   formatBytes(1500000)    → "1.4 MB"
 */
export function formatBytes(byteCount: number): string {
  // Less than 1 KB → show in bytes
  if (byteCount < BYTES_IN_KB) {
    return `${byteCount} B`
  }
  // Less than 1 MB → show in kilobytes, rounded to 1 decimal place
  if (byteCount < BYTES_IN_MB) {
    return `${(byteCount / BYTES_IN_KB).toFixed(1)} KB`
  }

  // 1 MB or more → show in megabytes, rounded to 1 decimal place
  return `${(byteCount / BYTES_IN_MB).toFixed(1)} MB`
}
