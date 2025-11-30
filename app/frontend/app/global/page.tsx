```
import { getGlobalList } from "@/lib/api";
import { GlobalGravityBowl } from "../../components/GlobalGravityBowl";
import { getGlobalList } from "../../lib/api";

export const dynamic = 'force-dynamic';

export default async function GlobalPage() {
  const globalList = await getGlobalList();

  return (
    <main className="page">
      <GlobalSection items={globalList.items} />
    </main>
  );
}
