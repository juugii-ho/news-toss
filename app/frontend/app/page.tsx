import { getGlobalList, getLocalList, getVsCard } from "../lib/api";
import { GlobalSection } from "../components/GlobalSection";
import { VsCardSection } from "../components/VsCardSection";
import { LocalMosaic } from "../components/LocalMosaic";
import { LocalGravityBowl } from "../components/LocalGravityBowl";

export const revalidate = 3600; // ISR: refresh every hour

export default async function HomePage() {
  const [globalList, vsCard, localList] = await Promise.all([
    getGlobalList(),
    getVsCard(),
    getLocalList()
  ]);

  return (
    <main className="page">
      <header className="section">
        <p className="chip chip-sky">뉴스토스 · PWA</p>
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 800, letterSpacing: "-0.02em" }}>
          글로벌 인사이트와 로컬 볼륨을 한눈에
        </h1>
        <p style={{ margin: 0, color: "var(--color-neutral-500)", lineHeight: 1.5 }}>
          목업 데이터를 기반으로 Hero/Compact 리스트, VS 카드, 모자이크 레이아웃을
          시각화했습니다. 이후 Supabase/API 연동 시 동일 구조로 교체합니다.
        </p>
      </header>

      <GlobalSection items={globalList.items} />
      <VsCardSection data={vsCard} />
      <LocalGravityBowl items={localList.items} />
      <LocalMosaic initial={localList} />
    </main>
  );
}
