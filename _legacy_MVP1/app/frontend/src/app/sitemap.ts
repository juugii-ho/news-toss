import { MetadataRoute } from 'next';
import { getSupabaseClient, isSupabaseConfigured } from '@/lib/supabase';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';

  const routes: MetadataRoute.Sitemap = [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1,
    },
  ];

  // Fetch topics from Supabase if configured
  if (isSupabaseConfigured()) {
    try {
      const supabase = getSupabaseClient();
      const { data: topics } = await supabase
        .from('mvp_topics')
        .select('id, date, created_at')
        .order('date', { ascending: false })
        .limit(100);

      if (topics) {
        topics.forEach((topic) => {
          routes.push({
            url: `${baseUrl}/topics/${topic.id}`,
            lastModified: new Date(topic.created_at || topic.date),
            changeFrequency: 'weekly',
            priority: 0.8,
          });
        });
      }
    } catch (error) {
      console.error('Error fetching topics for sitemap:', error);
    }
  }

  return routes;
}
