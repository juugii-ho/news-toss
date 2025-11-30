import { getGlobalList } from "@/lib/api";
import { GlobalSection } from "@/components/GlobalSection";

export const revalidate = 3600;

export default async function GlobalPage() {
  const globalList = await getGlobalList();

  return (
    <main className="page">
      <GlobalSection items={globalList.items} />
    </main>
  );
}
