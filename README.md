# 桃影热点

每天自动采集百度、微博、今日头条、小红书和腾讯公开热点榜，保存到 PostgreSQL，并通过 GitHub Pages 提供只读查询。

## 第一版能力

- 每天北京时间 09:15 自动采集，每个平台最多 100 条。
- 一个数据源失败不会影响其他数据源写入，执行结果会记录到数据库和 GitHub Actions 摘要。
- 每次采集后自动统计数据库容量；达到 400 MB 时在 GitHub Actions 中产生预警。
- 同一热点只保存一次正文信息，每天仅新增或更新排名快照。
- 支持平台筛选、日期查询、标题搜索和原文跳转。
- 浏览器只能调用有限分页的只读数据库函数，不能直接读写数据表。
- 未配置 Supabase 时展示带明显提示的示例数据，方便先确认页面效果。

## 项目结构

```text
collector/                 Python 多平台采集器
db/migrations/             PostgreSQL/Supabase 数据库迁移
src/                       React 热点网站
.github/workflows/         每日采集和 GitHub Pages 发布
tests/                     平台响应解析测试
```

## 一、创建 Supabase 数据库

1. 在 Supabase 创建一个项目。
2. 打开 **SQL Editor**。
3. 完整执行 `db/migrations/001_initial.sql`。
4. 在项目的 **Connect** 页面复制 PostgreSQL 连接字符串。
5. 使用连接字符串时，把其中的数据库密码替换成你自己设置的真实密码。

迁移会创建：

- `hot_topics`：热点标题、来源和原文地址。
- `hot_topic_snapshots`：每天的排名和热度。
- `collection_runs`：每次采集的成功、失败状态。
- `get_hot_topics`、`get_hot_source_summary`：前端唯一能调用的只读函数。

匿名用户没有三张数据表的直接访问权限，只能执行两个只读函数，而且单次最多返回 100 条。

## 二、配置 GitHub

进入仓库的 **Settings → Secrets and variables → Actions**。

### Secret

创建下面的 Repository secret：

| 名称 | 内容 |
| --- | --- |
| `DATABASE_URL` | Supabase PostgreSQL 连接字符串，包含数据库密码 |

### Variables

创建下面两个 Repository variables：

| 名称 | 内容 |
| --- | --- |
| `SUPABASE_URL` | 例如 `https://xxxx.supabase.co` |
| `SUPABASE_PUBLISHABLE_KEY` | Supabase 的 `sb_publishable_...` 公钥 |

Publishable Key 是给公开客户端使用的低权限标识，不是数据库密码；真正的数据库密码只保存在 `DATABASE_URL` Secret 中。

## 三、首次采集

1. 打开 GitHub 仓库的 **Actions**。
2. 选择 **每日采集热点**。
3. 点击 **Run workflow**。
4. 执行结束后，在任务摘要中确认每个平台的采集条数。

此后任务会每天自动运行。某个平台如果修改公开页面结构，会在采集状态中显示失败，但其他平台仍会继续保存。

任务摘要同时显示数据库已使用容量、500 MB 免费额度和使用率。达到 400 MB 后，工作流会生成“数据库容量预警”注解，但不会中断正常采集；达到 500 MB 时应清理历史数据或升级 Supabase 套餐。

## 四、发布 GitHub Pages

1. 进入 **Settings → Pages**。
2. 在 **Build and deployment** 中选择 **GitHub Actions**。
3. 打开 Actions 中的 **发布热点网站**，手动运行一次；后续推送到 `main` 会自动发布。
4. 网站地址通常为 `https://你的用户名.github.io/TaoYingHotPoint/`。

## 本地开发

前端：

```bash
pnpm install
cp .env.example .env.local
pnpm dev
```

采集器：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m collector.main --dry-run --limit 20
```

解析器测试：

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## 数据与合规说明

本项目只索引平台公开榜单中的标题、排名、热度、摘要、封面地址和原文链接，不保存文章正文，不绕过登录、验证码或其他访问控制。平台可能随时调整公开接口或反自动化规则；使用前应确认并遵守各平台当前服务条款、robots 规则及适用法律。
