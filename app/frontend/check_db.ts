
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = "https://gusmxyyzlchkdusmbsdk.supabase.co";
const supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1c214eXl6bGNoa2R1c21ic2RrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzQ0Mjc2OSwiZXhwIjoyMDc5MDE4NzY5fQ.nkHanSO9cD-GRh4IElqMRb-a9RAA-pc9xJUqwFQ2KAA";
const supabase = createClient(supabaseUrl, supabaseKey);

async function check() {
    const targetIds = [
        "30b53e67-cf2d-4817-948d-ff59fb8d7521",
        "1344c17c-a98b-4a17-8a93-40ee1150081c"
    ];

    const { data: topics, error } = await supabase
        .from("mvp2_topics")
        .select("*")
        .eq("id", "27d98245-eee2-4e1c-934a-7771e5f50a35")
        .limit(1);

    if (error) {
        console.error("Error fetching topics:", error);
        return;
    }

    if (topics && topics.length > 0) {
        const t = topics[0];
        console.log("Topic ID:", t.id);
        console.log("Thumbnail URL:", t.thumbnail_url);
        console.log("Summary:", t.summary);
    }
}

check();
