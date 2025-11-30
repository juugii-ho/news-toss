import { getLocalList } from "@/lib/api";
import { readLocalList } from "@/lib/mock";
import { LocalPageClient } from "@/components/LocalPageClient";

export const dynamic = 'force-dynamic';
export const revalidate = 0;

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
      <LocalPageClient country={country} data={safeLocal} />
    </main>
  );
}
