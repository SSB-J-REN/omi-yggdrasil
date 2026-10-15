// Calls Ollama's native chat API with a JSON schema so the reply is structured.
export async function chatJson(
  url: string,
  model: string,
  system: string,
  user: string,
  schema: object,
): Promise<unknown> {
  const res = await fetch(`${url}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model,
      stream: false,
      format: schema,
      options: { temperature: 0.8 },
      messages: [
        { role: "system", content: system },
        { role: "user", content: user },
      ],
    }),
  });
  if (!res.ok) throw new Error(`Ollama HTTP ${res.status}: ${await res.text()}`);
  const body = (await res.json()) as { message: { content: string } };
  return JSON.parse(body.message.content);
}
