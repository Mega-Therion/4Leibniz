import type { MetadataRoute } from 'next';
import { getWorks } from '@/lib/content';
import { env } from '@/lib/config';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const works = await getWorks();
  const staticRoutes = [
    '',
    '/works',
    '/guide',
    '/catalog',
    '/leibniz',
    '/leibniz/timeline',
    '/leibniz/concepts',
    '/leibniz/correspondents',
    '/about',
  ].map((path) => ({
    url: `${env.siteUrl}${path}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: path === '' ? 1 : 0.8,
  }));

  const workRoutes = works.map((w) => ({
    url: `${env.siteUrl}/works/${w.slug}`,
    lastModified: new Date(),
    changeFrequency: 'monthly' as const,
    priority: 0.9,
  }));

  return [...staticRoutes, ...workRoutes];
}
