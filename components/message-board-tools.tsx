'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

interface ModelContext {
  registerTool(
    tool: {
      name: string;
      title: string;
      description: string;
      inputSchema: object;
      annotations: {
        readOnlyHint: boolean;
        untrustedContentHint: boolean;
      };
      execute(input: unknown): Promise<unknown>;
    },
    options: { signal: AbortSignal },
  ): void | Promise<void>;
}

declare global {
  interface Document {
    readonly modelContext?: ModelContext;
  }
}

export function MessageBoardTools() {
  const router = useRouter();

  useEffect(() => {
    const context = document.modelContext;
    if (!context?.registerTool) return;

    const lifecycle = new AbortController();

    void Promise.resolve(
      context.registerTool(
        {
          name: 'create_message',
          title: 'Create message',
          description: 'Post one new anonymous message to the public board.',
          inputSchema: {
            type: 'object',
            properties: {
              message: {
                type: 'string',
                minLength: 1,
                maxLength: 500,
                description: 'The public message body.',
              },
            },
            required: ['message'],
            additionalProperties: false,
          },
          annotations: {
            readOnlyHint: false,
            untrustedContentHint: true,
          },
          async execute(input) {
            const message =
              typeof input === 'object' && input !== null && 'message' in input
                ? String(input.message).trim()
                : '';

            if (!message || message.length > 500) {
              throw new Error('Message must be between 1 and 500 characters.');
            }

            const response = await fetch(
              `/api/messages?message=${encodeURIComponent(message)}`,
            );

            if (!response.ok) {
              throw new Error('The message could not be posted.');
            }

            const result = (await response.json()) as { message: unknown };
            router.refresh();
            return result;
          },
        },
        { signal: lifecycle.signal },
      ),
    ).catch(() => undefined);

    return () => lifecycle.abort();
  }, [router]);

  return null;
}
