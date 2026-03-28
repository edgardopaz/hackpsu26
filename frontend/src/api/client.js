const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'

export async function analyzePost(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    let detail = 'Request failed.'

    try {
      const data = await response.json()
      detail = data.detail ?? detail
    } catch {
      // Fall back to the generic error message when the backend does not return JSON.
    }

    throw new Error(detail)
  }

  return response.json()
}

