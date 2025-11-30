```javascript
"use client";

import { redirect } from "next/navigation";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import HomePage from "./HomePage"; // This import seems to be a mistake if this file is HomePage itself. Assuming it's a wrapper.

export const dynamic = 'force-dynamic'; // Added dynamic export to force dynamic rendering
export const revalidate = 3600; // ISR: refresh every hour

export default async function HomePage() {
  redirect("/global");
}
```
