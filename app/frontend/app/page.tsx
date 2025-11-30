import GlobalPage from "./global/page";

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function HomePage() {
  return <GlobalPage />;
}
