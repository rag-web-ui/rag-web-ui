/**
 * Test for Issue #69: Maximum update depth exceeded during streaming
 *
 * This test verifies that the Answer component doesn't trigger infinite
 * re-renders when citations are updated rapidly during streaming.
 */

import React from 'react';
import { render, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Answer } from '../answer';

// Mock the API module
jest.mock('@/lib/api', () => ({
  api: {
    get: jest.fn(),
  },
}));

// Mock react-markdown and its plugins
jest.mock('react-markdown', () => {
  return function MockMarkdown({ children }: { children: string }) {
    return <div data-testid="markdown">{children}</div>;
  };
});

jest.mock('remark-gfm', () => ({}));
jest.mock('rehype-highlight', () => ({}));
jest.mock('react-file-icon', () => ({
  FileIcon: () => <div>FileIcon</div>,
}));

describe('Answer Component - Issue #69 Fix', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  it('should debounce citation fetching during rapid updates', async () => {
    const { api } = require('@/lib/api');

    // Mock API responses
    api.get.mockResolvedValue({
      name: 'Test KB',
      file_name: 'test.pdf',
    });

    const initialCitations = [
      {
        id: 1,
        text: 'Citation 1',
        metadata: { kb_id: 1, document_id: 1 },
      },
    ];

    // Render with initial citations
    const { rerender } = render(
      <Answer markdown="Test content [citation](1)" citations={initialCitations} />
    );

    // Simulate rapid streaming updates (like what happens during LLM streaming)
    const updates = 10;
    for (let i = 0; i < updates; i++) {
      act(() => {
        rerender(
          <Answer
            markdown={`Test content ${i} [citation](1)`}
            citations={[
              {
                id: 1,
                text: `Citation ${i}`,
                metadata: { kb_id: 1, document_id: 1 },
              },
            ]}
          />
        );
      });
    }

    // Fast-forward through debounce delay (300ms)
    act(() => {
      jest.advanceTimersByTime(350);
    });

    // Wait for async operations
    await waitFor(() => {
      expect(api.get).toHaveBeenCalled();
    });

    // With debounce, API calls should be significantly reduced
    // Without debounce, it would be called 20 times (10 updates * 2 API calls each)
    // With debounce, it should be called much fewer times (ideally 2-4)
    const callCount = api.get.mock.calls.length;
    expect(callCount).toBeLessThan(10); // Much less than 20 (without debounce)
  });

  it('should not cause infinite re-renders with many rapid updates', async () => {
    const { api } = require('@/lib/api');

    api.get.mockResolvedValue({
      name: 'Test KB',
      file_name: 'test.pdf',
    });

    const renderSpy = jest.fn();

    function TestWrapper({ citations }: { citations: any[] }) {
      renderSpy();
      return <Answer markdown="Test" citations={citations} />;
    }

    const { rerender } = render(<TestWrapper citations={[]} />);

    // Simulate 50 rapid updates (simulating streaming)
    for (let i = 0; i < 50; i++) {
      act(() => {
        rerender(
          <TestWrapper
            citations={[
              {
                id: 1,
                text: `Citation ${i}`,
                metadata: { kb_id: 1, document_id: 1 },
              },
            ]}
          />
        );
      });
    }

    // Fast-forward debounce
    act(() => {
      jest.advanceTimersByTime(300);
    });

    await waitFor(() => {
      expect(api.get).toHaveBeenCalled();
    });

    // Render count should be reasonable (initial + 50 updates + potential state updates)
    // but NOT hundreds or thousands (which would indicate infinite loop)
    expect(renderSpy).toHaveBeenCalledTimes(51); // Initial + 50 updates
  });

  it('should eventually fetch citation info after streaming stops', async () => {
    const { api } = require('@/lib/api');

    const mockKB = { name: 'Knowledge Base 1' };
    const mockDoc = { file_name: 'document.pdf' };

    api.get.mockImplementation((url: string) => {
      if (url.includes('/documents/')) {
        return Promise.resolve(mockDoc);
      }
      return Promise.resolve(mockKB);
    });

    const citations = [
      {
        id: 1,
        text: 'Test citation',
        metadata: { kb_id: 1, document_id: 1 },
      },
    ];

    render(<Answer markdown="Test [citation](1)" citations={citations} />);

    // Fast-forward through debounce delay
    act(() => {
      jest.advanceTimersByTime(300);
    });

    // Wait for API calls to complete
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/api/knowledge-base/1');
      expect(api.get).toHaveBeenCalledWith('/api/knowledge-base/1/documents/1');
    });
  });
});
