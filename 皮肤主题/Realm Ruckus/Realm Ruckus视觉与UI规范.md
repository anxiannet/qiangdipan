# Realm Ruckus 视觉与UI规范

适用规则版本：V1.3  
更新时间：2026-07-14

## 一、文件定位

本文件维护 Realm Ruckus 的皮肤专属视觉语言、英文卡面布局和资产统一要求。

通用尺寸、出血、安全区和印刷规则仍以：

```text
规范流程/视觉总规范.md
规范流程/UI规范.md
```

为唯一来源。

## 二、产品视觉定位

```text
Chunky Cartoon Fantasy
Playful, collectible, readable and action-driven
```

核心气质：

- 欢乐怪物混战
- 厚重3D手办感
- 明快、非血腥
- 强动作、强表情、强轮廓
- 桌面与手机缩略图均可识别
- 所有资产看起来属于同一款产品

禁止：

- 黑暗写实恐怖
- 严肃史诗战争
- 纯角色站姿海报
- 百科卡或测试版UI
- 直接模仿现有知名IP的角色、Logo、字体或卡框
- 保留与Realm Ruckus无关的西游建筑、祥云、汉字牌匾和道教法器

## 三、卡牌尺寸

| 类型 | 方向 | 成品尺寸 | 含3mm出血画布 |
|---|---|---:|---:|
| Monster | 竖版 | 63 × 88 mm | 69 × 94 mm / 815 × 1110 px |
| Relic | 竖版 | 63 × 88 mm | 69 × 94 mm / 815 × 1110 px |
| Territory | 横版 | 88 × 63 mm | 94 × 69 mm / 1110 × 815 px |
| Guide | 竖版 | 63 × 88 mm | 69 × 94 mm / 815 × 1110 px |

所有关键文字、脸部、星级、卡号和核心道具必须进入通用安全区。

## 四、英文卡面信息层级

### Monster Card

从上到下建议：

1. Stars
2. Illustration
3. Horizontal English nameplate
4. Skill icon
5. English card text
6. RRK card code

不得沿用中文竖排名称栏。英文卡名必须横排。

### Relic Card

1. Relic类别标识
2. Relic主体插画
3. Horizontal English nameplate
4. Effect icon
5. English card text
6. RRK card code

### Territory Card

1. Realm emblem
2. Realm name
3. Territory scene
4. Territory name
5. RRK card code

Territory没有技能区和技能图标。

## 五、英文排版规则

- 卡名优先单行，必要时最多两行。
- 卡名与技能文案使用易读的拉丁字体，不使用难辨认的伪中世纪花体作为正文。
- 标题字体可以有手工、石刻或木牌感，但必须清楚。
- 技能文案使用sentence case。
- Stars、数量和规则关键词必须在实体尺寸下清晰。
- RRK卡号置于低视觉权重位置，但必须可读。
- 先制作最长名称和最长技能文案的压力测试卡，再锁定字号。

建议压力测试对象：

```text
The Restless Cemetery
Return 2 Defenders of 2 Stars or lower to their owners' hands.
Call a player by name. If they respond, each of you draws 1 card, then discards 1 card.
```

## 六、星级视觉

Stars是规则数值，不是单纯稀有度。

- 1-Star：基础银铁、简单结构。
- 2-Star：强化银铁，增加少量材质细节。
- 3-Star：明显精英感，可加入金属镶边。
- 4-Star：重型领主感，增加体积与装饰层级。
- 5-Star：传奇首领感，但不得遮挡Stars或技能信息。

同一Star等级的卡框强度必须统一。

## 七、四个Realm视觉系统

| Realm | 徽章方向 | 主色 | 环境材质 |
|---|---|---|---|
| The Bonewilds | 骨冠或裂纹头骨山形 | 骨白、冷灰、幽蓝 | 风化石、骨塔、幽光 |
| The Emberlands | 火山裂口或燃烧铁砧 | 橙红、炭黑、铜金 | 熔岩、焦岩、锻炉 |
| The Ironfang Range | 双兽牙或山峰盾徽 | 岩灰、铁黑、土黄 | 巨石、铁铆钉、兽牙 |
| The Webwood | 蛛网月轮或藤蔓眼 | 森林绿、紫、月光银 | 巨树、蛛丝、蘑菇、泉水 |

Realm颜色只能帮助识别，不得暗示Monster阵营或额外规则。

## 八、Monster美术要求

每张Monster插画必须包含：

- 清晰主角
- 与技能一致的动作
- 明确表情
- 可识别道具或特效
- 可理解的目标或结果
- 与同星级和同种族角色不同的剪影

技能视觉示例：

| 机制 | 视觉表现 |
|---|---|
| Return your Defender | 招手撤回、绳索拉回或紧急撤退 |
| Draw then discard | 翻找零件、挑选物品并扔掉旧物 |
| View a hand card | 偷窥、望远镜或从肩后探看 |
| Call by name | 扩音器、回声魔法或高声呼喊 |
| Defeat | 击飞、压制、吓跑，不使用血腥 |
| Return to hand | 风浪、弹簧、冲击波将目标送走 |
| Take a Defender | 抓走、诱骗、套索或搬运 |
| Immediate Deploy | 首领召来另一只Monster |
| Immediate Raid | 从高处俯冲或吹响进攻号角 |

## 九、Relic美术要求

Relic必须以物件为主体，不画成普通装备展示。

- The Echo Flask：有可视化回声、名字呼唤和被回应的对象。
- Nullstone Ring：表现吸收、打断或冻结其他魔法效果。
- Snarecoil：表现自动缠绕并拖走目标。
- Emberguard Dome：表现覆盖一个Territory的防护罩。

Relic插画不得暗示超出卡面文字的目标数量、持续时间或伤害。

## 十、Territory美术要求

- 横版地图场景感。
- 无角色主导、无技能区。
- 同一Realm的3张牌共享材质和色彩，但地形轮廓必须明显不同。
- 缩小后仍能通过主地标区分12块Territory。
- 场景中可出现小型Monster活动增加趣味，但不得造成控制权或规则误解。

## 十一、卡背

至少需要两套卡背：

```text
Main Deck Back
Territory Deck Back
```

要求：

- 从桌面远距离明显区分。
- 不使用正反方向可被识别的非对称细节，避免洗牌后泄露方向。
- Main Deck突出Realm Ruckus Logo与怪物混战符号。
- Territory Deck突出四Realm地图或四徽章结构。
- 不显示QDP关联信息。

## 十二、Guide视觉

- 英文横排。
- 大标题、分区标题和步骤数字清晰。
- 使用Deploy、Raid、Relic、Stars和Territory Reset功能图标辅助阅读。
- 图标不替代规则文字。
- 先做实体尺寸打印测试，再确认字号和行距。

## 十三、交付检查

每张成品卡必须确认：

- 尺寸、出血和安全区正确
- 英文拼写与标点正确
- 卡名与卡表一致
- 技能文案与卡表一致
- Stars正确
- 插画与技能一致
- RRK卡号正确
- 无QDP或后台映射信息
- 无裁切线、安全线和测试标记
- 缩略图和实体尺寸均可读
