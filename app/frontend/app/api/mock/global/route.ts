import { NextResponse } from "next/server";
import path from "node:path";
import { promises as fs } from "node:fs";

export async function GET() {
  const filePath = path.join(process.cwd(), "outputs", "mock_data", "global_list.json");
  const file = await fs.readFile(filePath, "utf-8");
  const data = JSON.parse(file);
  return NextResponse.json(data, { status: 200 });
}
