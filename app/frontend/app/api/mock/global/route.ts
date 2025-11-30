import { readGlobalList } from "@/lib/mock";
import { NextResponse } from "next/server";

export const dynamic = 'force-dynamic';

export async function GET() {
  const data = await readGlobalList();
  return NextResponse.json(data, { status: 200 });
}
