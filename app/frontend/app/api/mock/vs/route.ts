import { readVsCard } from "@/lib/mock";
import { NextResponse } from "next/server";

export const dynamic = 'force-dynamic';

export async function GET() {
  const data = readVsCard();
  return NextResponse.json(data, { status: 200 });
}
