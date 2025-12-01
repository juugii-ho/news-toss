import { getGlobalList } from "@/lib/api";
import { GlobalSection } from "@/components/GlobalSection";

import { Suspense } from "react";

export const revalidate = 3600;

export default async function GlobalPage() {
  const globalList = await getGlobalList();

  return (
    <main className="page">
      <Suspense fallback={null}>
        <GlobalSection items={globalList.items} />
      </Suspense>
    </main>
  );
}
