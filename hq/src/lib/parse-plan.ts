import type { ParsedJob } from "./types";

function normalize(markdown: string): string {
  return markdown.replace(/\r\n/g, "\n").replace(/\r/g, "\n").trim();
}

function firstLineTitle(text: string): { title: string; body: string } {
  const lines = text.split("\n");
  const title = (lines[0] ?? "").replace(/^#{1,6}\s+/, "").trim();
  const body = lines.slice(1).join("\n").trim();
  return { title: title || "Untitled job", body };
}

function extractCheckboxes(markdown: string): ParsedJob[] {
  const lines = markdown.split("\n");
  const jobs: ParsedJob[] = [];
  let current: { title: string; extra: string[] } | null = null;

  const flush = () => {
    if (!current) return;
    jobs.push({
      title: current.title,
      body: current.extra.join("\n").trim(),
    });
    current = null;
  };

  for (const line of lines) {
    const match = line.match(/^\s*[-*]\s+\[(?: |x|X)\]\s+(.+)$/);
    if (match) {
      flush();
      current = { title: match[1].trim(), extra: [] };
      continue;
    }
    if (current) {
      current.extra.push(line);
    }
  }
  flush();
  return jobs.filter((job) => job.title.length > 0);
}

function extractHeadings(markdown: string): ParsedJob[] {
  const chunks = markdown.split(/^#{1,3}\s+/m).map((chunk) => chunk.trim());
  const jobs: ParsedJob[] = [];
  for (const chunk of chunks) {
    if (!chunk) continue;
    const parsed = firstLineTitle(chunk);
    if (parsed.title === "Untitled job" && !parsed.body) continue;
    jobs.push(parsed);
  }
  return jobs;
}

function extractNumbered(markdown: string): ParsedJob[] {
  const parts = markdown.split(/^\s*\d+\.\s+/m).map((part) => part.trim());
  const jobs: ParsedJob[] = [];
  for (const part of parts) {
    if (!part) continue;
    jobs.push(firstLineTitle(part));
  }
  return jobs;
}

function extractParagraphs(markdown: string): ParsedJob[] {
  return markdown
    .split(/\n{2,}/)
    .map((block) => block.trim())
    .filter(Boolean)
    .map(firstLineTitle);
}

export function parsePlan(markdown: string): ParsedJob[] {
  const text = normalize(markdown);
  if (!text) return [];

  const checkboxes = extractCheckboxes(text);
  if (checkboxes.length > 0) return checkboxes;

  const headings = extractHeadings(text);
  if (headings.length > 1) return headings;

  const numbered = extractNumbered(text);
  if (numbered.length > 1) return numbered;

  const paragraphs = extractParagraphs(text);
  if (paragraphs.length > 1) return paragraphs;

  return [firstLineTitle(text)];
}
