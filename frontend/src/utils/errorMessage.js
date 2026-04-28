export function getErrorMessage(error, fallback) {
  if (error instanceof Error && error.message) {
    return `${fallback}: ${error.message}`;
  }

  return fallback;
}
