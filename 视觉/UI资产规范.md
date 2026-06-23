# 《抢地盘》UI资产规范

## 文件定位

本文件定义《抢地盘》可复用 UI 资产。

目的：

- AI 批量生成
- Figma 设计
- Photoshop 合成
- 网页卡牌展示
- 实体印刷

本文件只定义 UI 资产拆分与生成要求，不定义：

- 游戏规则
- 技能效果
- 卡牌数量
- 世界观设定

相关文件：

- `视觉/视觉总规范.md`
- `视觉/视觉锚点规范.md`
- `视觉/卡牌框架规范.md`
- `视觉/UI修订说明-地盘横置方案.md`
- `规则/V1.2-基础卡表.md`
- `规则/V1.2-卡面技能文案.md`

---

# 核心原则

UI 与插画分离。

所有 UI 资产必须：

- PNG
- 透明背景
- 无文字
- 无角色主体
- 无技能描述
- 无妖怪名称
- 无地盘名称
- 无攻击力
- 无防守力
- 无编号
- 无水印

后续通过程序合成：

```text
插画 + UI + 名称 + 技能
```

生成最终卡牌。

---

# 目录结构

```text
视觉/UI资产/
├── monster/
├── artifact/
├── land/
├── back/
├── common/
└── README.md
```

---

# 一、妖怪卡 UI

目录：

```text
视觉/UI资产/monster/
```

## 必须生成资产

```text
ui_monster_frame_common.png
ui_monster_skill_scroll.png
ui_star_1.png
ui_star_2.png
ui_star_3.png
ui_name_plate_short.png
ui_name_plate_long.png
```

---

## ui_monster_frame_common.png

用途：妖怪卡通用立体边框。

要求：

- 透明背景
- 竖版比例 63 × 88 mm
- 300 dpi
- 3 mm 出血
- 暗金浮雕边框
- 四角立体角饰
- 妖纹花纹
- 金属厚度
- 中央留空给插画
- 不包含名称
- 不包含技能文字
- 不包含星级

视觉方向：

- 商品级收藏卡
- 国风幻想
- 妖云纹理
- 暗金金属
- 非资料卡风格
- 非 Word 表格风格

---

## ui_monster_skill_scroll.png

用途：妖怪技能描述底部卷轴。

要求：

- 透明背景
- 卷轴 / 石碑 / 妖纹铭牌风格
- 可放一行技能文案
- 不包含任何文字
- 不包含技能名
- 不包含句号

---

## ui_star_1.png / ui_star_2.png / ui_star_3.png

用途：妖怪卡左上角星级。

要求：

- 透明背景
- 金属浮雕星
- 高对比
- 缩略图可识别
- 分别显示 1 颗、2 颗、3 颗星
- 不包含数字
- 不包含文字

位置要求：

星级固定放在卡面左上角。

不得放在顶部中央。

不得放在名称下方。

---

## ui_name_plate_short.png

用途：短名妖怪名称牌匾。

适用：

```text
牛魔王
白骨精
红孩儿
黄袍怪
青狮精
```

要求：

- 透明背景
- 适合 2 至 4 字名称
- 浮雕书法牌匾
- 金色描边
- 暗金底纹
- 不包含文字

---

## ui_name_plate_long.png

用途：长名妖怪名称牌匾。

必须支持：

```text
金鼻白毛老鼠精
```

要求：

- 透明背景
- 至少容纳 7 个中文字
- 不裁切
- 不压缩
- 不强制换行
- 比短名牌匾更宽
- 不包含文字

---

# 二、法宝卡 UI

目录：

```text
视觉/UI资产/artifact/
```

## 必须生成资产

```text
ui_artifact_frame.png
ui_artifact_skill_plate.png
ui_artifact_type_badge.png
```

---

## ui_artifact_frame.png

用途：法宝卡立体边框。

要求：

- 透明背景
- 竖版比例 63 × 88 mm
- 300 dpi
- 3 mm 出血
- 紫金神兵边框
- 法阵纹样
- 四角立体角饰
- 中央留空给法宝插画
- 不包含名称
- 不包含技能文字
- 不包含星级

视觉方向：

- 法器
- 神兵
- 紫金
- 法阵
- 宝光
- 与妖怪卡属于同一世界观背景体系

---

## ui_artifact_skill_plate.png

用途：法宝技能铭牌。

要求：

- 透明背景
- 紫金铭牌
- 法器铭文感
- 可放一行法宝效果文案
- 不包含任何文字

---

## ui_artifact_type_badge.png

用途：法宝类型徽记。

要求：

- 透明背景
- 小型法宝视觉徽记
- 尽量用图形表达
- 不写文字
- 法阵 / 神兵 / 宝光风格

---

# 三、地盘卡 UI

目录：

```text
视觉/UI资产/land/
```

地盘卡为横版。

尺寸方向：

```text
88 × 63 mm
```

说明：

地盘卡与妖怪、法宝尺寸相同，只是方向不同。

---

## 必须生成资产

```text
ui_land_frame.png
ui_land_title_plate.png
ui_land_faction_badge_baigu.png
ui_land_faction_badge_huoyun.png
ui_land_faction_badge_shituo.png
ui_land_faction_badge_pansi.png
```

---

## ui_land_frame.png

用途：横版地盘卡边框。

要求：

- 透明背景
- 横版比例 88 × 63 mm
- 300 dpi
- 3 mm 出血
- 领地边框
- 山河纹
- 四角角饰
- 中央大面积留空给地盘场景
- 不包含地名
- 不包含技能区
- 不包含星级

视觉方向：

- 地图
- 山川
- 洞府
- 领地
- 横向全景
- 不使用妖怪卡背景体系
- 不使用法宝卡背景体系

---

## ui_land_title_plate.png

用途：地盘名称牌匾。

要求：

- 透明背景
- 横版牌匾
- 可容纳 4 字地名
- 山头 / 洞府 / 地图纹样
- 不包含文字

---

## 地盘阵营徽记

文件：

```text
ui_land_faction_badge_baigu.png
ui_land_faction_badge_huoyun.png
ui_land_faction_badge_shituo.png
ui_land_faction_badge_pansi.png
```

要求：

- 透明背景
- 不写文字
- 白骨：骨纹 / 鬼火
- 火云：火焰 / 云纹
- 狮驼：狮首 / 妖城门
- 盘丝：蛛网 / 毒纹

---

# 四、卡背 UI

目录：

```text
视觉/UI资产/back/
```

---

## ui_deck_back.png

用途：妖怪卡与法宝卡共用卡背。

适用：

- 妖怪卡
- 法宝卡

原因：

妖怪与法宝属于同一公共牌库。

玩家抽牌前不能通过卡背区分抽到的是妖怪还是法宝。

要求：

- 透明背景版本
- 竖版比例 63 × 88 mm
- 妖云
- 群山
- 暗金浮雕
- 夕妖风格中心纹章
- 不写“妖怪牌”
- 不写“法宝牌”
- 不区分妖怪与法宝

禁止生成：

```text
ui_monster_back.png
ui_artifact_back.png
monster_back.png
artifact_back.png
```

---

## ui_land_back.png

用途：地盘卡独立卡背。

适用：

- 地盘牌库

要求：

- 透明背景版本
- 横版比例 88 × 63 mm
- 地图
- 山川
- 领地印章
- 暗金边框
- 与公共牌库卡背明显区分
- 不写文字

---

# 五、通用 UI

目录：

```text
视觉/UI资产/common/
```

## 必须生成资产

```text
ui_corner_gold.png
ui_corner_silver.png
ui_corner_bronze.png
ui_corner_purple_gold.png

ui_trim_gold.png
ui_trim_silver.png
ui_trim_bronze.png
ui_trim_purple_gold.png
```

---

## 角饰

用途：不同等级角饰。

要求：

- 透明背景
- 立体浮雕
- 可复用

对应关系：

- gold：3星首领 / 高级装饰
- silver：2星精英
- bronze：1星小妖
- purple_gold：法宝

---

## 边框花纹条

用途：边框连续花纹。

要求：

- 透明背景
- 可横向或纵向拼接
- 连续花纹
- 立体金属感

---

# 六、最终合成顺序

最终卡牌合成顺序：

1. 插画底图
2. 卡框
3. 星级或类型徽记
4. 名称牌匾
5. 技能卷轴或铭牌
6. 文字

文字必须由合成脚本后置写入。

UI 资产本身不得预写文字。

---

# 七、质量要求

所有资产必须：

- 透明背景 PNG
- 无文字
- 无乱码
- 无角色主体
- 无妖怪名称
- 无技能文字
- 无攻击力
- 无防守力
- 无阵营文字
- 无编号
- 无水印
- 无白底
- 无黑底

视觉必须：

- 商品级
- 有厚度
- 有金属感
- 有浮雕感
- 有层次
- 非平面 UI
- 非资料卡风格
- 非 Word 表格风格
- 非百科卡风格

---

# 八、后续维护原则

本文件是《抢地盘》UI 透明资产生成与合成的唯一来源。

若后续 UI 资产命名、目录结构、卡背策略发生变化，必须先更新本文件，再执行批量生成。