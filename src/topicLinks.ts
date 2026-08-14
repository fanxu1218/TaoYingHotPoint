import type { HotTopic, SourceKey } from './types'

const SOURCE_DOMAINS: Record<SourceKey, string> = {
  baidu: 'baidu.com',
  weibo: 'weibo.com',
  toutiao: 'toutiao.com',
  xiaohongshu: 'xiaohongshu.com',
  tencent: 'qq.com',
}

export function fallbackSearchUrl(topic: HotTopic): string {
  return `https://www.baidu.com/s?wd=${encodeURIComponent(topic.title)}`
}

export function primaryTopicUrl(topic: HotTopic): string | null {
  try {
    const url = new URL(topic.url)
    if (url.protocol !== 'http:' && url.protocol !== 'https:') {
      return null
    }

    const sourceDomain = SOURCE_DOMAINS[topic.source]
    if (url.hostname !== sourceDomain && !url.hostname.endsWith(`.${sourceDomain}`)) {
      return null
    }

    if (topic.source === 'toutiao' && (url.hostname === 'toutiao.com' || url.hostname.endsWith('.toutiao.com'))) {
      url.search = ''
      url.hash = ''
    }

    if (topic.source === 'tencent' && url.hostname === 'view.inews.qq.com') {
      const articleId = url.pathname.match(/^\/a\/([^/]+)/)?.[1]
      if (articleId) return `https://news.qq.com/rain/a/${articleId}`
    }

    return url.toString()
  } catch {
    return null
  }
}
