import { redirect } from "next/navigation";

export const revalidate = 3600; // ISR: refresh every hour

export default async function HomePage() {
  redirect("/global");
}
