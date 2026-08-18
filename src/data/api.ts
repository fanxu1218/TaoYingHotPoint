import { demoTopics } from './demo'
import { prepareTopics } from './topicList'
import { SOURCES, type HotTopic, type HotTopicPage, type SourceKey, type SourceSummary } from '../types'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string | undefined
const publishableKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY as string | undefined

interface RpcHotTopic {
  id: number
  source: SourceKey
  title: string
  url: string
  summary: string | null
  cover_url: string | null
  rank: number
  hot_score: number | null
  captured_at: string
}

interface RpcSourceSummary {
  source: SourceKey
  item_count: number
  latest_captured_at: string | null
}

async function callRpc<T>(name: string, body: Record<string, string | number | null>): Promise<T> {
  if (!supabaseUrl || !publishableKey) {
    throw new Error('Supabase 尚未配置')
  }

  const response = await fetch(`${supabaseUrl}/rest/v1/rpc/${name}`, {
    method: 'POST',
    headers: {
      apikey: publishableKey,
      Authorization: `Bearer ${publishableKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    throw new Error(`数据服务返回 ${response.status}`)
  }
  return response.json() as Promise<T>
}

export async function fetchHotTopics(date: string, source: SourceKey | 'all'): Promise<HotTopicPage> {
  if (!supabaseUrl || !publishableKey) {
    const topics = prepareTopics(source === 'all' ? demoTopics : demoTopics.filter((topic) => topic.source === source))
    return {
      topics,
      summary: SOURCES.map((item) => ({
        source: item,
        itemCount: demoTopics.filter((topic) => topic.source === item).length,
        latestCapturedAt: demoTopics.find((topic) => topic.source === item)?.capturedAt ?? null,
      })),
      demo: true,
    }
  }

  const topicRequests = source === 'all'
    ? SOURCES.map((item) => callRpc<RpcHotTopic[]>('get_hot_topics', {
        p_date: date,
        p_source: item,
        p_limit: 100,
        p_offset: 0,
      }))
    : [callRpc<RpcHotTopic[]>('get_hot_topics', {
        p_date: date,
        p_source: source,
        p_limit: 100,
        p_offset: 0,
      })]

  const [rowGroups, sourceRows] = await Promise.all([
    Promise.all(topicRequests),
    callRpc<RpcSourceSummary[]>('get_hot_source_summary', { p_date: date }),
  ])
  const rows = rowGroups.flat()

  const topics = prepareTopics(rows.map((row): HotTopic => ({
    id: row.id,
    source: row.source,
    title: row.title,
    url: row.url,
    summary: row.summary,
    coverUrl: row.cover_url,
    rank: row.rank,
    hotScore: row.hot_score,
    capturedAt: row.captured_at,
  })))
  const summary: SourceSummary[] = sourceRows.map((row) => ({
    source: row.source,
    itemCount: row.item_count,
    latestCapturedAt: row.latest_captured_at,
  }))

  return { topics, summary, demo: false }
}
