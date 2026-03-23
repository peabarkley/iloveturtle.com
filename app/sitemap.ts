// app/sitemap.ts
import { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  // 基础URL
  const baseUrl = 'https://www.iloveturtle.com'
  
  // 静态页面路由
  const staticRoutes = [
    '',
    '/species',
    '/care',
    '/disease',
    '/aquascape',
    '/share'
  ].map(route => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: route === '' ? 1 : 0.8,
  }))
  
  // 动态路由示例：龟种档案页面
  // 如果你有文章列表API，可以在这里fetch动态生成
  const speciesList = [
    'musk-turtle',
    'razorback-musk-turtle',
    'narrow-bridged-musk-turtle'
    // ... 更多龟种slug
  ]
  
  const dynamicRoutes = speciesList.map(slug => ({
    url: `${baseUrl}/species/${slug}`,
    lastModified: new Date(),
    changeFrequency: 'monthly' as const,
    priority: 0.7,
  }))
  
  return [...staticRoutes, ...dynamicRoutes]
}
