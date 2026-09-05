import { listMessages } from '@/db/messages';
import { MessageBoardTools } from '@/components/message-board-tools';

export const dynamic = 'force-dynamic';

function formatTimestamp(value: string) {
  const date = new Date(value.endsWith('Z') ? value : `${value}Z`);

  return new Intl.DateTimeFormat('en', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    timeZone: 'UTC',
    timeZoneName: 'short',
  }).format(date);
}

export default async function Home() {
  const messages = await listMessages();

  return (
    <main className="mx-auto min-h-screen w-full max-w-2xl border-x border-white/10 bg-card/35">
      <MessageBoardTools />
      <header className="sticky top-0 z-10 flex items-center justify-between border-b border-white/10 bg-background/90 px-5 py-4 backdrop-blur-xl sm:px-7">
        <div>
          <h1 className="text-lg font-semibold tracking-tight text-foreground">Public board</h1>
          <p className="mt-0.5 font-mono text-xs uppercase tracking-[0.16em] text-muted-foreground">
            No accounts · everything is public
          </p>
        </div>
        <span className="rounded-full border border-cyan-300/25 bg-cyan-300/10 px-2.5 py-1 font-mono text-xs text-cyan-200">
          {messages.length} {messages.length === 1 ? 'message' : 'messages'}
        </span>
      </header>

      <section aria-labelledby="compose-heading" className="border-b border-white/10 p-5 sm:p-7">
        <h2 id="compose-heading" className="sr-only">Add a message</h2>
        <form action="/post" method="get" className="space-y-3">
          <label htmlFor="message" className="block text-sm font-medium text-slate-200">Add to the board</label>
          <textarea
            id="message"
            name="message"
            required
            maxLength={500}
            rows={3}
            placeholder="What do you want everyone to know?"
            className="block w-full resize-y rounded-xl border border-white/15 bg-black/25 px-4 py-3 text-base leading-6 text-foreground shadow-inner outline-none placeholder:text-slate-500 focus:border-cyan-300/60 focus:ring-2 focus:ring-cyan-300/15"
          />
          <div className="flex items-center justify-between gap-4">
            <p className="font-mono text-xs text-muted-foreground">Submitted with an HTTP GET request</p>
            <button
              type="submit"
              className="rounded-lg bg-cyan-300 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-200 focus-visible:ring-offset-2 focus-visible:ring-offset-background active:translate-y-px"
            >
              Post message
            </button>
          </div>
        </form>
      </section>

      <section aria-labelledby="timeline-heading">
        <h2 id="timeline-heading" className="sr-only">All messages</h2>
        {messages.length === 0 ? (
          <div className="px-5 py-20 text-center sm:px-7">
            <p className="text-base font-medium text-slate-300">Nothing here yet.</p>
            <p className="mt-1 text-sm text-muted-foreground">Post the first message above.</p>
          </div>
        ) : (
          <ol>
            {messages.map((message) => (
              <li key={message.id} className="border-b border-white/10 px-5 py-5 sm:px-7">
                <article>
                  <div className="mb-2 flex items-center gap-2 text-sm">
                    <span aria-hidden="true" className="grid h-8 w-8 place-items-center rounded-full bg-gradient-to-br from-cyan-300/25 to-blue-500/25 font-mono text-xs text-cyan-100">A</span>
                    <div>
                      <p className="font-semibold text-slate-200">anonymous</p>
                      <time dateTime={`${message.createdAt}Z`} className="block font-mono text-xs text-muted-foreground">
                        {formatTimestamp(message.createdAt)}
                      </time>
                    </div>
                  </div>
                  <p className="whitespace-pre-wrap break-words text-base leading-7 text-slate-100">{message.body}</p>
                  <p className="mt-3 font-mono text-xs text-slate-600">#{message.id}</p>
                </article>
              </li>
            ))}
          </ol>
        )}
      </section>
    </main>
  );
}
