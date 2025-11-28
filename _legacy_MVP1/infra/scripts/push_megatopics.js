#!/usr/bin/env node
/**
 * Push aggregated megatopics JSON into Supabase tables (topics, topic_country_stats).
 * Usage:
 *   SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... node infra/scripts/push_megatopics.js [path/to/final_megatopics.json]
 *
 * Notes:
 * - Requires service role key (anon key cannot insert).
 * - If a topic with the same date+title exists, it reuses the existing id and replaces its stats.
 * - Countries must already exist in the countries table (see infra/supabase/migrations).
 */

const fs = require("fs/promises");
const path = require("path");

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const TOPICS_TABLE = process.env.SUPABASE_TOPICS_TABLE || "topics";
const TOPIC_STATS_TABLE = process.env.SUPABASE_TOPIC_STATS_TABLE || "topic_country_stats";
// Default to "title", but allow overriding (e.g., "title_kr") via env
const TITLE_COLUMN = process.env.SUPABASE_TITLE_COLUMN || "title";
const INPUT_PATH =
  process.argv[2] || path.join(__dirname, "../../data/pipelines/final_megatopics.json");

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables.");
  process.exit(1);
}

async function supabaseRequest(method, endpoint, body, headers = {}) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${endpoint}`, {
    method,
    headers: {
      apikey: SUPABASE_SERVICE_ROLE_KEY,
      Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
      "Content-Type": "application/json",
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${method} ${endpoint} failed: ${res.status} ${res.statusText} - ${text}`);
  }
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return res.json();
  }
  return null;
}

async function findTopicId(date, title) {
  const endpoint = `${TOPICS_TABLE}?date=eq.${encodeURIComponent(date)}&${TITLE_COLUMN}=eq.${encodeURIComponent(
    title
  )}&select=id`;
  const existing = await supabaseRequest("GET", endpoint);
  if (Array.isArray(existing) && existing.length > 0) {
    return existing[0].id;
  }
  return null;
}

async function insertTopic(date, title, summary = null, thumbnail_url = null, titleKr = null) {
  const topicPayload = { date, summary, thumbnail_url };
  // Primary title column (configurable)
  topicPayload[TITLE_COLUMN] = title;
  // If a Korean title exists, include it when using non-KR primary column to avoid loss
  if (titleKr && TITLE_COLUMN !== "title_kr") {
    topicPayload.title_kr = titleKr;
  }

  const payload = [topicPayload];
  const inserted = await supabaseRequest("POST", TOPICS_TABLE, payload, {
    Prefer: "return=representation",
  });
  if (!Array.isArray(inserted) || !inserted[0]?.id) {
    throw new Error("Insert topic returned unexpected response");
  }
  return inserted[0].id;
}

async function replaceStats(topicId, statsObj) {
  // delete existing stats for this topic id
  await supabaseRequest("DELETE", `${TOPIC_STATS_TABLE}?topic_id=eq.${topicId}`);

  const rows = Object.entries(statsObj).map(([country_code, counts]) => ({
    topic_id: topicId,
    country_code,
    supportive_count: counts.supportive || 0,
    factual_count: counts.factual || 0,
    critical_count: counts.critical || 0,
    summary: counts.summary || null,
  }));

  if (rows.length === 0) return;

  await supabaseRequest("POST", TOPIC_STATS_TABLE, rows);
}

async function main() {
  console.log(`Reading megatopics from ${INPUT_PATH}`);
  const raw = await fs.readFile(INPUT_PATH, "utf-8");
  const megatopics = JSON.parse(raw);

  for (const topic of megatopics) {
    const { date, title, title_kr = null, summary = null, thumbnail_url = null, stats = {} } = topic;
    const formattedDate = date || new Date().toISOString().slice(0, 10);

    const titleValue = title_kr || title;
    let topicId = await findTopicId(formattedDate, titleValue);
    if (topicId) {
      console.log(`Updating existing topic: "${titleValue}" (${formattedDate})`);
    } else {
      console.log(`Inserting topic: "${titleValue}" (${formattedDate})`);
      topicId = await insertTopic(formattedDate, titleValue, summary, thumbnail_url, title_kr);
    }

    await replaceStats(topicId, stats);
  }

  console.log(`Completed: processed ${megatopics.length} topics.`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
