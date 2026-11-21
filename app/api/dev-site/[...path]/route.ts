// The site's files, read-only, out of content/.
//
// On the live site this is the FastAPI router in backend/dev_site.py, which
// reads the same names out of a private S3 bucket and also takes the owner
// panel's uploads. Here it only serves: the owner panel can open, but saving
// needs the real backend (it answers 501 with a note saying so).

import { readFile } from "node:fs/promises";
import path from "node:path";

const ROOT = path.join(process.cwd(), "content");

// The same narrow list the backend allows, nothing else in the folder.
const ALLOWED =
  /^(?:(?:thumb|full)\/p\d{2,3}\.webp|profile(?:-alt)?\.webp|RANK_AFF_UG_2023\.pdf|album\.json|milestones\.json|site\.json|music\.json|music\/[a-z0-9-]{1,48}\.(?:mp3|m4a|ogg)|resume\/(?:Pandian_Sambath_Resume\.(?:pdf|docx)|page-\d\.webp|thumb\.webp|resume\.json))$/;

const TYPES: Record<string, string> = {
  ".webp": "image/webp",
  ".pdf": "application/pdf",
  ".json": "application/json",
  ".mp3": "audio/mpeg",
  ".m4a": "audio/mp4",
  ".ogg": "audio/ogg",
  ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
};

async function serve(req: Request, parts: string[], head: boolean) {
  const name = parts.join("/");
  if (!ALLOWED.test(name)) return new Response("Not found", { status: 404 });
  try {
    const body = await readFile(path.join(ROOT, name));
    const ext = path.extname(name);
    const headers: Record<string, string> = {
      "Content-Type": TYPES[ext] ?? "application/octet-stream",
      "Content-Length": String(body.length),
      "Cache-Control": ext === ".json" ? "no-store" : "public, max-age=3600",
    };
    if (new URL(req.url).searchParams.has("download")) headers["Content-Disposition"] = `attachment; filename="${path.basename(name)}"`;
    return new Response(head ? null : new Uint8Array(body), { headers });
  } catch {
    return new Response("Not found", { status: 404 });
  }
}

type Ctx = { params: Promise<{ path: string[] }> };

export async function GET(req: Request, { params }: Ctx) {
  return serve(req, (await params).path, false);
}

export async function HEAD(req: Request, { params }: Ctx) {
  return serve(req, (await params).path, true);
}

const READ_ONLY = () =>
  Response.json(
    { detail: "This mirror is read-only. Uploads and edits run on the live site's backend (backend/dev_site.py)." },
    { status: 501 },
  );
export const POST = READ_ONLY;
export const PUT = READ_ONLY;
