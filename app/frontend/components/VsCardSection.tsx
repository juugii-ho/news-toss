import type { VsCard } from "../lib/mock";

const stanceColors = {
  POSITIVE: { bg: "var(--color-positive-bg)", text: "var(--color-positive-text)" },
  NEGATIVE: { bg: "var(--color-negative-bg)", text: "var(--color-negative-text)" },
  NEUTRAL: { bg: "var(--color-neutral-bg)", text: "var(--color-neutral-text)" }
} as const;

type Props = {
  data: VsCard;
};

export function VsCardSection({ data }: Props) {
  return (
    <section className="section">
      <div className="section-header">
        <h2>VS 카드 (Bubble Battle)</h2>
        <span className="chip chip-sky">국가별 관점</span>
      </div>

      <div className="vs-card">
        <div className="vs-header">
          <p className="vs-label">질문</p>
          <h3>{data.title_ko}</h3>
          <p className="vs-intro">{data.intro_ko}</p>
        </div>
        <div className="vs-bubbles">
          {data.perspectives.map((p) => {
            const colors = stanceColors[p.stance];
            return (
              <article
                key={p.country_code}
                className="bubble"
                style={{ backgroundColor: colors.bg, color: colors.text }}
              >
                <div className="bubble-header">
                  <span className="bubble-flag">{p.flag_emoji}</span>
                  <span className="bubble-country">{p.country_name}</span>
                </div>
                <p className="bubble-line">{p.one_liner_ko}</p>
                <a className="bubble-link" href={p.source_link} target="_blank" rel="noreferrer">
                  원문 보기 ↗
                </a>
              </article>
            );
          })}
        </div>
        <div className="vs-articles">
          <p className="vs-label">관련 기사</p>
          <ul>
            {data.related_articles.map((a) => (
              <li key={a.url}>
                <a href={a.url} target="_blank" rel="noreferrer">
                  {a.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
