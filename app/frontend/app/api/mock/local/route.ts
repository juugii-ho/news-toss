import { NextRequest, NextResponse } from "next/server";
import path from "node:path";
import { promises as fs } from "node:fs";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const page = Number(searchParams.get("page") || "1");

  const filePath = path.join(process.cwd(), "outputs", "mock_data", "local_list.json");
  const file = await fs.readFile(filePath, "utf-8");
  const baseData = JSON.parse(file) as {
    country: string;
    page: number;
    items: any[];
    hasNextPage: boolean;
  };

  // For mock pagination, return same dataset but tweak ids/titles per page.
  const items = baseData.items.map((item) => ({
    ...item,
    topic_id: `${item.topic_id}_p${page}`
  }));

  return NextResponse.json(
    {
      country: baseData.country,
      page,
      items,
      hasNextPage: page < 2 ? true : false
    },
    { status: 200 }
  );
}
