import { Hono } from "hono";

const app = new Hono();

app.get("/", (c) => c.json({ name: "Cloudflare Pages" }));

export const onRequest = async (context: any) => {
  return await app.fetch(context.request);
};