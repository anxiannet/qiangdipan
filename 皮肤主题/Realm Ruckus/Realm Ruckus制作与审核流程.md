# Realm Ruckus 制作与审核流程

适用规则版本：V1.3  
更新时间：2026-07-14

## 一、定位

本文件规定 Realm Ruckus 从命名、英文文案、插画、UI、卡号到印刷交付的执行顺序。

所有规则冲突以 `规则/V1.3-核心规则.md` 和 `规则/V1.3-基础卡表.md` 为准。

## 二、生产顺序

1. 锁定规则版本与卡表版本。
2. 审核产品名、宣传语和RRK前缀。
3. 审核四个Realm、角色、Relic和Territory名称。
4. 审核英文术语表。
5. 完成英文核心规则和指南卡一致性检查。
6. 锁定每张卡的英文卡面文案。
7. 建立单卡美术需求。
8. 完成角色概念与插画。
9. 完成Monster、Relic、Territory、Guide和卡背UI。
10. 完成卡面合成。
11. 对每个唯一卡面分配RRK卡号。
12. 进行语言、规则、视觉、印刷四轮审核。
13. 输出审核图和clean印刷图。
14. 制作实体样卡并试玩。
15. 根据反馈修订；任何卡面内容变化均分配新卡号。

## 三、命名审核

每个名称必须检查：

- 英语母语者是否易读、易念、易记
- 是否与角色外形或技能气质一致
- 是否存在不必要的双关、冒犯或文化误解
- 是否与其他卡名过度相似
- 是否明显撞用知名IP、桌游或电子游戏名称
- 是否适合印在卡面和包装上

产品名、Logo和正式前缀投入印刷前必须进行商标检索。

## 四、英文文案审核

按以下顺序：

1. 对照QDP机制卡确认效果边界。
2. 使用统一术语。
3. 优先短句、主动语态和明确目标。
4. 检查数字、Stars、所有格和单复数。
5. 检查“exactly”与“up to”的规则差异。
6. 由至少一名熟悉桌游英语的审核者复核。
7. 将最终文案写入 `Realm Ruckus标准版卡表.md`。

禁止只在图片中修改文字而不更新卡表。

## 五、单卡美术需求模板

```text
Source mechanic card:
Realm Ruckus name:
Stars:
Card effect:
Creature / object type:
Body shape and silhouette:
Personality:
Main action:
Facial expression:
Primary prop:
Scene:
Effect visualization:
UI safe-area requirements:
Must differ from:
Forbidden elements:
Current art status:
```

## 六、插画审核

每张图逐项检查：

| 项目 | 合格标准 |
|---|---|
| 主体识别 | 1秒内识别主角或Relic |
| 技能一致性 | 动作、目标和结果与卡面效果一致 |
| 轮廓差异 | 不像其他卡的换色版本 |
| 表情与喜剧感 | 明确、夸张但不低俗 |
| 非血腥 | 无写实伤害、残肢或恐怖表现 |
| Realm一致性 | 场景材质符合世界观 |
| UI安全 | 脸、手、道具和特效不被UI遮挡 |
| IP独立性 | 无明显复制现有角色或品牌元素 |

不合格图保留为历史版本，不覆盖。

## 七、卡面审核

```text
卡名：
Source card：
RRK card code：
英文名称：合格 / 不合格
英文文案：合格 / 不合格
Stars与类型：合格 / 不合格
插画与技能：合格 / 不合格
UI安全区：合格 / 不合格
字号与可读性：合格 / 不合格
卡背体系：合格 / 不合格
后台映射：合格 / 不合格
是否含不应显示的QDP信息：是 / 否
是否需要新卡号：是 / 否
问题说明：
```

## 八、RRK卡号分配

只有最终唯一卡面完成后才分配RRK卡号。

后台至少记录：

```text
mechanic_id
skin_id
card_code
source_card_code
rules_effect_id
art_version
text_version
language
status
```

卡面完全相同的复制卡共用卡号。

插画、名称、文案、语言、Stars、图标、边框、版式或其他实际印刷内容变化时，必须分配新卡号。

旧卡号标记为historical、retired或test，不得复用。

## 九、指南卡审核

- 四面内容覆盖开局、目标、回合、行动、Raid、Combat、Territory Reset和Endgame。
- 与英文核心规则使用相同术语。
- 不重复维护完整技能表。
- 63 × 88 mm实体打印后可读。
- Guide Card A为Guide 1/2正反面；Guide Card B为Guide 3/4正反面。

## 十、包装审核

包装至少包含：

- Realm Ruckus Logo
- 宣传语
- 2–4 Players
- 15–30 Minutes
- 建议年龄，待合规评估后确定
- 组件数量
- 简短目标与玩法说明
- 版权、制造、条码和警告信息预留
- Main Deck、Territory和实际玩法示意

包装不得暗示未包含的组件、模式或扩展。

## 十一、印刷审核

- 300 dpi
- 四边3 mm出血
- 关键内容在安全区
- 最终图无裁切线、安全线、测试字样或水印
- Main Deck与Territory Deck卡背可明显区分
- 同一牌库卡背完全一致，不能通过背面识别卡牌
- 英文黑位、细线、渐变和暗部进行实体打样检查
- 完成至少一轮真实尺寸洗牌、阅读和桌面识别测试

## 十二、完成定义

Realm Ruckus达到“可印刷试玩”状态，必须同时满足：

- 40张Main Deck卡面完成
- 12张Territory卡面完成
- 2张双面Guide卡完成
- Main Deck与Territory Deck卡背完成
- 英文核心规则完成
- 全部RRK卡号和后台映射完成
- 语言、规则、视觉和印刷审核全部通过
- 实体样卡试玩无阻断性问题
