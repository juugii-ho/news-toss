import { getLocalList } from "@/lib/api";
import { readLocalList } from "@/lib/mock";
import { LocalPageClient } from "@/components/LocalPageClient";

import { Suspense } from "react";

export const revalidate = 3600;

type Props = {
  searchParams: { country?: string };
};

export default async function LocalPage({ searchParams }: Props) {
  const country = searchParams.country || "ALL";
  const localList = await getLocalList({ country }).catch(async () => readLocalList());
  const safeLocal =
    localList && Array.isArray((localList as any).items) ? localList : await readLocalList();

  return (
    <main className="page">
      <Suspense fallback={null}>
        <LocalPageClient country={country} data={safeLocal} />
      </Suspense>
    </main>
  );
}
