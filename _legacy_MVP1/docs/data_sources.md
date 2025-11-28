# Data Sources & Feed Status

## RSS Feeds (News)

| Country | Source | URL | Status | Notes |
|---------|--------|-----|--------|-------|
| **US** | NYT (World) | `https://rss.nytimes.com/services/xml/rss/nyt/World.xml` | ✅ Active | |
| **US** | Washington Post | `https://main.rss.reuters.com/Reuters/WorldNews` | ✅ Active | Replaced WaPo with Reuters due to paywall/structure issues |
| **GB** | BBC (World) | `http://feeds.bbci.co.uk/news/world/rss.xml` | ✅ Active | |
| **GB** | The Guardian | `https://www.theguardian.com/world/rss` | ✅ Active | |
| **FR** | France 24 | `https://www.france24.com/en/rss` | ⚠️ Unstable | Frequent 403 Forbidden (User-Agent sensitive) |
| **FR** | Le Monde | `https://www.lemonde.fr/en/rss/une.xml` | ✅ Active | |
| **DE** | DW | `https://rss.dw.com/rdf/rss-en-all` | ⚠️ Unstable | Connection timeouts observed |
| **DE** | Spiegel | `https://www.spiegel.de/international/index.rss` | ✅ Active | |
| **IT** | ANSA | `https://www.ansa.it/english/sito/ansait_rss.xml` | ✅ Active | |
| **CA** | CBC | `https://www.cbc.ca/cmlink/rss-world` | ✅ Active | |
| **JP** | NHK World | `https://www3.nhk.or.jp/rss/news/cat0.xml` | ❌ Failed | 404 Not Found (URL needs update) |
| **JP** | Japan Times | `https://www.japantimes.co.jp/feed/topstories` | ✅ Active | |
| **KR** | Korea Herald | `http://www.koreaherald.com/common_prog/rss/rss_config.php?ct=102` | ✅ Active | |
| **KR** | Hankyoreh | `http://www.hani.co.kr/rss/` | ❌ Failed | 404/Encoding issues |
| **CN** | Xinhua | `http://www.xinhuanet.com/english/rss/world.xml` | ❌ Failed | 403 Forbidden |
| **CN** | SCMP | `https://www.scmp.com/rss/91/feed` | ✅ Active | |
| **RU** | Moscow Times | `https://www.themoscowtimes.com/rss/news` | ✅ Active | |
| **RU** | RT | `https://www.rt.com/rss/news/` | ✅ Active | |

## APIs

| Service | Purpose | Model | Status | Notes |
|---------|---------|-------|--------|-------|
| **Gemini API** | Embedding | `text-embedding-004` | ✅ Active | |
| **Gemini API** | Stance/Translation | `gemini-2.5-flash` | ✅ Active | Batch size 50 + Retry logic applied |
| **Supabase** | Database | PostgreSQL | ✅ Active | `mvp_topics`, `mvp_articles` |

## Known Issues
- **France24 / Xinhua**: Strict anti-bot protection. May need rotating proxies or alternative feeds.
- **NHK / Hani**: Dead URLs. Need to find replacements.
