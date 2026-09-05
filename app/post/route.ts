import { addMessage } from '@/db/messages';

export async function GET(request: Request) {
  const url = new URL(request.url);
  const message = url.searchParams.get('message')?.trim() ?? '';

  if (!message || message.length > 500) {
    return new Response('Message must be between 1 and 500 characters.', { status: 400 });
  }

  await addMessage(message);
  return Response.redirect(new URL('/', request.url), 303);
}
