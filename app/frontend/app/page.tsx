import GlobalPage from "./global/page";

export const revalidate = 3600;

export default async function HomePage() {
  return <GlobalPage />;
}
