import { env } from 'cloudflare:workers';

export interface Message {
  id: number;
  body: string;
  createdAt: string;
}

function database() {
  if (!env.DB) {
    throw new Error('The DB binding is unavailable.');
  }

  return env.DB;
}

export async function listMessages(): Promise<Message[]> {
  const result = await database()
    .prepare(
      `SELECT id, body, created_at AS createdAt
       FROM messages
       ORDER BY created_at DESC, id DESC`,
    )
    .all<Message>();

  return result.results;
}

export async function addMessage(body: string): Promise<Message> {
  const result = await database()
    .prepare(
      `INSERT INTO messages (body)
       VALUES (?)
       RETURNING id, body, created_at AS createdAt`,
    )
    .bind(body)
    .first<Message>();

  if (!result) {
    throw new Error('The message could not be created.');
  }

  return result;
}
