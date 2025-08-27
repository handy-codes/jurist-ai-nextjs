import { NextRequest, NextResponse } from "next/server";
import { loadQaSummary } from "../../../../lib/db";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get("session_id") || undefined;

    // Use the function from lib/db
    const summary = await loadQaSummary(sessionId);

    return NextResponse.json(summary || { coherence: 0, legal: 0, context: 0 });
  } catch (error) {
    console.error("Error fetching metrics:", error);
    return NextResponse.json(
      { error: "Failed to fetch metrics" },
      { status: 500 }
    );
  }
}
