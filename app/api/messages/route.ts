import { addMessage, listMessages } from '@/db/messages';

export async function GET(request: Request) {
  const url = new URL(request.url);
  const rawMessage = url.searchParams.get('message') ?? url.searchParams.get('text');

  if (rawMessage === null) {
    return Response.json({ messages: await listMessages() });
  }

  const message = rawMessage.trim();
  if (!message || message.length > 500) {
    return Response.json(
      { error: 'Message must be between 1 and 500 characters.' },
      { status: 400 },
    );
  }

  const created = await addMessage(message);
  return Response.json({ message: created }, { status: 201 });
}
