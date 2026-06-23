// mock_codebase/app/apiClient.js

/**
 * Fetches tasks from the API.
 * 
 * Baseline version:
 * - Does not accept query options (status, limit, offset).
 * - Expects a raw JSON array back.
 */
export async function fetchTasks(baseUrl) {
  const response = await fetch(`${baseUrl}/api/tasks`);
  if (!response.ok) {
    throw new Error('Failed to fetch tasks');
  }
  const data = await response.json();
  return data; // Assumes raw array: [ {id, title, status}, ... ]
}
