// mock_codebase/tests/apiClient.test.js
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchTasks } from '../app/apiClient.js';

describe('fetchTasks client helper', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('should fetch tasks without parameters and return formatted output', async () => {
    const mockEnvelope = {
      items: [
        { id: '1', title: 'Task 1', status: 'completed' },
        { id: '2', title: 'Task 2', status: 'pending' }
      ],
      total: 2,
      limit: 10,
      offset: 0
    };

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockEnvelope,
    });
    vi.stubGlobal('fetch', fetchMock);

    const result = await fetchTasks('http://localhost:8000');

    expect(fetchMock).toHaveBeenCalledWith('http://localhost:8000/api/tasks');
    expect(result).toEqual({
      tasks: mockEnvelope.items,
      total: mockEnvelope.total
    });
  });

  it('should pass pagination and filtering query parameters', async () => {
    const mockEnvelope = {
      items: [{ id: '2', title: 'Task 2', status: 'pending' }],
      total: 1,
      limit: 2,
      offset: 1
    };

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockEnvelope,
    });
    vi.stubGlobal('fetch', fetchMock);

    const result = await fetchTasks('http://localhost:8000', {
      status: 'pending',
      limit: 2,
      offset: 1
    });

    const expectedUrl = 'http://localhost:8000/api/tasks?status=pending&limit=2&offset=1';
    expect(fetchMock).toHaveBeenCalledWith(expectedUrl);
    expect(result).toEqual({
      tasks: mockEnvelope.items,
      total: mockEnvelope.total
    });
  });

  it('should throw error when api request fails', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
    });
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchTasks('http://localhost:8000')).rejects.toThrow('Failed to fetch tasks');
  });
});
