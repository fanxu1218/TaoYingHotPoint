export const SOURCES = ['baidu', 'weibo', 'toutiao', 'xiaohongshu', 'tencent'] as const

export type SourceKey = (typeof SOURCES)[number]

export interface HotTopic {
  id: number
  source: SourceKey
  title: string
  url: string
  summary: string | null
  coverUrl: string | null
  rank: number
  hotScore: number | null
  capturedAt: string
}

export interface SourceSummary {
  source: SourceKey
  itemCount: number
  latestCapturedAt: string | null
}

export interface HotTopicPage {
  topics: HotTopic[]
  summary: SourceSummary[]
  demo: boolean
}
