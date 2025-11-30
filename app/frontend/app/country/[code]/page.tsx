import { SupabaseNewsService } from "../../../lib/supabase-service";
import { LocalMosaic } from "../../../components/LocalMosaic";
import { LocalGravityBowl } from "../../../components/LocalGravityBowl";

export const revalidate = 3600; // ISR

interface Props {
    params: {
        code: string;
    };
}

export default async function CountryPage({ params }: Props) {
    const countryCode = params.code.toUpperCase();

    // Fetch real local data
    const localList = await SupabaseNewsService.getTopics(countryCode);

    return (
        <main className="page">
            <header className="section">
                <p className="chip chip-sky">Local Insight · {countryCode}</p>
                <h1 style={{ margin: 0, fontSize: 24, fontWeight: 800, letterSpacing: "-0.02em" }}>
                    {countryCode} Trending Topics
                </h1>
            </header>

            <LocalGravityBowl items={localList.items} />
            <LocalMosaic initial={localList} />
        </main>
    );
}
