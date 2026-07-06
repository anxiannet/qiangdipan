# 《夕妖：抢地盘》Codex 实现边界

## 文件定位

本文件用于约束 Codex 或其他代码实现工具在 `web/` 工程中的自由发挥空间。

本文件只规定实现边界、允许路由、禁止路由、数据来源、页面组件要求和验收清单。

本文件不修改规则，不新增卡牌，不维护第二份卡表，不替代现有设计与规则文件。

---

## 一、实现前必读顺序

实现网站页面骨架前，按以下顺序读取：

```text
1. 当前项目记忆.md
2. 网站/网站地图.md
3. 网站/文档位置统一规划.md
4. 网站/官网页面结构设计.md
5. 网站/正式官网首页设计稿.md
6. 网站/正式官网首页内容设计.md
7. 网站/官网视觉美术风格设计.md
8. 网站/官网UI组件规范.md
9. 网站/网站技术栈方案.md
10. 网站/网站目录位置约定.md
11. 网站/网站部署状态.md
```

如文件之间冲突，以以下顺序为准：

```text
当前项目记忆.md
↓
网站/网站地图.md
↓
网站/Codex实现边界.md
↓
网站/文档位置统一规划.md
↓
网站/官网页面结构设计.md
```

---

## 二、当前核心结论

网站采用分散具体页面体系。

```text
卡牌资料在 /cards
规则资料在 /rules
技能评级在 /rules/skills 与 /rules/skill-rating
美术与插画在 /art
印刷生产在 /print
众筹运营在 /crowdfunding
网站开发在 /devlog/website
```

不建立集中资料入口。

不建立前端 Markdown 内容库。

不复制规则、卡表或技能为第二份前端内容。

---

## 三、允许创建的一级路由

第一阶段允许：

```text
/
/cards
/rules
/play
/print
/art
/crowdfunding
/devlog
```

第二阶段预留：

```text
/account
```

除以上路由及其明确子路由外，不得新增一级入口。

---

## 四、允许创建的子路由

### 1. 卡牌

```text
/cards/monster
/cards/treasure
/cards/territory
/cards/:id
/cards/history
/cards/backup
/cards/candidates
/cards/expansions
```

### 2. 规则

```text
/rules/base
/rules/duel
/rules/cards
/rules/skills
/rules/skill-rating
/rules/skill-history
/rules/history
/rules/deprecated
/rules/future
/rules/manual
/rules/quick-reference
```

### 3. 试玩

```text
/play/tutorial
/play/pve
/play/duel
/play/local
/play/lobby
/play/room/:roomId
```

### 4. 印刷成果

```text
/print/assets
/print/box
/print/box-back-copy
/print/box-dieline-reference
/print/production-note
```

### 5. 美术档案

```text
/art/visual-spec
/art/ui-spec
/art/illustration-review-flow
/art/card-final-review-flow
/art/box-size-spec
/art/illustration-history
/art/card-art-history
/art/character-design-history
```

### 6. 众筹预热

```text
/crowdfunding/presale-plan
/crowdfunding/playtest-feedback
/crowdfunding/content-plan
```

### 7. 开发记录

```text
/devlog/rules
/devlog/art
/devlog/print
/devlog/website
/devlog/roadmap
/devlog/website/architecture
/devlog/website/page-structure
/devlog/website/sitemap
/devlog/website/tech-stack
/devlog/website/deployment-status
/devlog/website/online-play-tech
```

---

## 五、禁止创建的路由与目录

严禁创建：

```text
/docs
/library
/wiki
/archive
/admin
/database
/posts
/blog，除非后续明确要求
/content
/content/docs
/web/content
/web/content/docs
/web/markdown
/web/docs
/web/library
```

严禁在前台出现以下概念：

```text
文档中心
资料馆
文档详情
文档列表
Markdown 文件
文件夹浏览
```

---

## 六、允许的数据来源

页面可以读取或由构建脚本转换以下来源：

```text
当前项目记忆.md
规则/当前规则.md
规则/V1.2-基础卡表.md
规则/V1.2-技能汇总表.md
规则/V1.2-技能评分标准.md
规则/未来扩展与双人对战计划.md
妖怪志/卡名/卡名.md
法宝志/法宝名/法宝名.md
规范流程/视觉总规范.md
规范流程/UI规范.md
规范流程/插画审核流程.md
规范流程/成品卡审核流程.md
规范流程/包装盒尺寸规范.md
包装盒/包装盒背面文案.md
包装盒/天地盖硬盒刀模参考说明.md
运营/众筹与预售计划.md
web/public/assets/print/v1/manifest.json
web/public/assets/print/v1/cards/
web/public/assets/print/v1/box/
web/public/assets/print/v1/docs/
```

明确任务才读取：

```text
规则/游戏手册.md
规则/指南卡.md
卡牌成品/印刷说明.md
备选方案/*
规则历史/*
美术历史/*
```

---

## 七、禁止复制的数据

严禁在前端组件、页面、常量或手写 JSON 中复制维护：

```text
第二份规则全文
第二份基础卡表
第二份技能表
第二份技能评分标准
第二份玩家手册
第二份指南卡
第二份印刷说明
第二份备选卡表
```

允许生成：

```text
只读 JSON
构建产物
索引数据
路由映射
图片 manifest 读取结果
```

但生成数据必须能追溯到仓库源文件，不得手写成为新的来源。

---

## 八、页面必须包含的导航组件

所有官网层页面必须包含：

```text
SiteHeader
SiteFooter
Breadcrumbs，首页除外
RelatedPagesBlock
ContinueReadingBlock
```

长页面建议包含：

```text
SectionNav
OnThisPage
PrevNextNav
```

游戏层页面例外：

```text
/play 及其子路由可以使用 GameShell，不使用完整 SiteFooter。
```

---

## 九、页面关联硬性规则

### 1. 当前规则页

`/rules/base` 必须关联：

```text
/rules/history
/rules/skills
/rules/skill-rating
/cards
/rules/future
/rules/manual
/rules/quick-reference
```

### 2. 技能评分页

`/rules/skill-rating` 必须关联：

```text
/rules/skills
/rules/skill-history
/cards
/rules/future
```

### 3. 单卡卡志页

`/cards/:id` 必须关联：

```text
/cards/history
/rules/skills
/rules/skill-rating
/art/illustration-history
同阵营或同类型卡牌
```

### 4. 美术规范页

`/art/visual-spec` 必须关联：

```text
/art/illustration-review-flow
/art/illustration-history
/art/card-final-review-flow
/cards
```

### 5. 规则变化历史页

`/rules/history` 必须关联：

```text
/rules/base
/rules/skills
/rules/skill-rating
/rules/future
```

### 6. 印刷成果页

`/print` 必须关联：

```text
/print/assets
/print/box
/print/production-note
```

---

## 十、占位页标准

第一阶段允许占位页，但占位页不得空白、不得工程化。

占位页必须包含：

```text
页面标题
当前状态
预计用途
返回上级入口
相关页面入口
继续阅读入口
```

占位页不得出现：

```text
TODO
Coming soon
Placeholder
Lorem ipsum
未实现
施工中，除非作为用户可读的项目状态说明
Markdown
Docs
Library
```

---

## 十一、视觉实现边界

必须遵守：

```text
网站/官网视觉美术风格设计.md
网站/官网UI组件规范.md
```

允许自由发挥：

```text
组件拆分方式
CSS 类名
响应式实现方式
加载状态表现
空状态视觉
页面内卡片排列
代码组织方式
```

禁止自由发挥：

```text
整体视觉风格
主导航结构
路由命名
页面归属
内容来源
规则解释
卡牌数据
是否出现 /docs 或 /library
是否建立 Markdown 内容库
```

---

## 十二、内容与规则边界

Codex 不得：

```text
修改规则文件
修改基础卡表
新增卡牌
新增星级
新增技能
新增阵营
新增胜利条件
新增商城、抽卡、排行榜、NFT、支付系统
把玩家展示文件当成规则来源
把生产说明当成规则或官网文案来源
```

固定核心规则表达：

```text
控制同一妖域 3 块地盘，立即获胜。
```

---

## 十三、第一阶段实现范围

第一阶段只搭页面骨架与导航关系：

```text
/
/cards
/cards/:id，占位
/cards/history，占位
/cards/backup，占位
/rules
/rules/base，占位
/rules/skills，占位
/rules/skill-rating，占位
/rules/history，占位
/rules/future，占位
/rules/manual，占位
/rules/quick-reference，占位
/play
/print
/art
/art/illustration-history，占位
/crowdfunding
/devlog
/devlog/roadmap，占位
```

第一阶段不做：

```text
/account
正式支付
商城
抽卡
排行榜
NFT
完整联网房间
复杂权限系统
在线编辑资料
全文搜索
版本 diff
评论系统
```

---

## 十四、验收清单

实现完成后必须检查：

```text
1. 不存在 /docs 路由。
2. 不存在 /library 路由。
3. 不存在 web/content/docs 或类似 Markdown 内容库。
4. 一级导航只有：首页、卡牌、规则、试玩、印刷成果、美术档案、众筹预热、开发记录。
5. /cards 有卡牌图鉴、单卡卡志、备选卡表、卡牌历史入口。
6. /rules 有基础规则、技能汇总、技能评分、规则历史、未来计划、玩家版说明入口。
7. /art 有视觉规范、插画审核、插画历史入口。
8. /print 有印刷成果、资源清单、包装、生产说明入口。
9. 每个具体页面有相关页面和继续阅读。
10. 占位页不是空白页，也不是工程 TODO 页。
11. 未新增规则、卡牌、技能、星级、阵营、胜利条件。
12. 未复制维护第二份规则、卡表或技能表。
13. 页面视觉符合蓝金西游桌游风与非Q版妖怪方向。
```

---

## 十五、当前结论

Codex 可以自由实现代码结构和组件细节。

Codex 不可以自由设计信息架构、路由体系、内容来源、规则解释、卡牌数据或前台资料组织方式。

实现阶段必须以 `网站/网站地图.md` 和本文件为准。
