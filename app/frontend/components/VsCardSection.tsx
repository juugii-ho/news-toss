import type { VsCard } from "../lib/mock";

type Props = {
  data: VsCard;
};

export function VsCardSection({ data }: Props) {
  const articles =
    data.related_articles?.map((a) => ({
      ...a,
      source: a.source || a.url?.split("/")[2] || "언론사",
      title_original: (a as any).title_original,
      title_ko: (a as any).title_ko,
      country_code: (a as any).country_code
    })) ?? [];
  const grouped = articles.reduce<Record<string, typeof articles>>((acc, cur) => {
    const key = cur.country_code || "기타";
    if (!acc[key]) acc[key] = [];
    acc[key].push(cur);
    return acc;
  }, {});

  return (
    <section className="section">
      <div className="rounded-card" style={{ padding: "var(--space-5)" }}>
        <p className="vs-label">질문</p>
        <h3 style={{ margin: "var(--space-2) 0", fontSize: "20px", fontWeight: 800, letterSpacing: "-0.01em" }}>
          {data.title_ko}
        </h3>
        {data.intro_ko ? (
          <p className="vs-intro" style={{ marginTop: "var(--space-2)" }}>
            {data.intro_ko}
          </p>
        ) : null}
      </div>

      {data.description_ko ? (
        <div className="rounded-card" style={{ padding: "var(--space-5)" }}>
          <p className="vs-label">설명</p>
          <p className="vs-intro" style={{ marginTop: "var(--space-2)", lineHeight: 1.6 }}>
            {data.description_ko}
          </p>
        </div>
      ) : null}

      <div className="rounded-card" style={{ padding: "var(--space-5)" }}>
        <p className="vs-label" style={{ marginBottom: "var(--space-3)" }}>관련 기사</p>
        {articles.length > 0 ? (
          Object.entries(grouped).map(([source, items]) => (
            <div key={source} style={{ marginTop: "var(--space-4)" }}>
              <p style={{
                margin: "0 0 var(--space-3)",
                fontSize: 14,
                fontWeight: 800,
                color: "var(--color-primary-700)",
                letterSpacing: "-0.01em"
              }}>
                {source}
              </p>
              <ul className="article-list">
                {items.map((a) => (
                  <li key={a.url} className="article-item">
                    <a href={a.url} target="_blank" rel="noreferrer" className="article-link">
                      <h4 style={{ marginBottom: "var(--space-1)" }}>
                        {a.title_ko || a.title}
                        <span style={{
                          color: "var(--color-neutral-500)",
                          fontSize: 12,
                          marginLeft: "var(--space-2)",
                          fontWeight: 600
                        }}>
                          - {a.source}
                        </span>
                      </h4>
                      {a.published_at ? (
                        <div className="article-meta">
                          <span>{new Date(a.published_at).toLocaleDateString("ko-KR")}</span>
                        </div>
                      ) : null}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))
        ) : (
          <p className="status-text" style={{ marginBottom: 0 }}>
            관련 기사가 없습니다.
          </p>
        )}
      </div>
    </section>
  );
}
