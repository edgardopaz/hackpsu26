const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'

/**
 * Analyze a social media post using either a screenshot or a link
 * @param {File | null} file - Image file for screenshot mode
 * @param {string} link - Social media URL for link mode
 * @returns {Promise<Object>} Analysis results with framing, coverage, and neutral summary
 * @throws {Error} If the API request fails
 */
export async function analyzePost(file = null, link = '') {
  const formData = new FormData()
  
  // Screenshot mode: send file
  if (file) {
    formData.append('file', file)
  } 
  // Link mode: send URL
  else if (link) {
    formData.append('post_link', link)
  }
  // Validation happens in App.jsx, but double-check here
  else {
    throw new Error('Either a file or a link is required')
  }

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

