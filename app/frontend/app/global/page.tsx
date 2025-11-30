import { getGlobalList } from "@/lib/api";
import { GlobalSection } from "@/components/GlobalSection";

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function GlobalPage() {
  const globalList = await getGlobalList();

  return (
    <main className="page">
      <GlobalSection items={globalList.items} />
    </main>
  );
}
