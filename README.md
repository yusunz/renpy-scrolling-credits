# Ren'Py 通用滚动字幕

一个自包含的 Ren'Py 滚动字幕组件：内容以**恒定速度**从屏幕底部向上滚动，滚动时长由内容高度自动计算，不需要手工设置"滚几秒钟"。可用于片尾字幕、制作人员名单、汉化名单、鸣谢名单等场景。

整个组件只有 `scrolling_credits_auto.rpy` 一个文件，复制进任意 Ren'Py 项目的 `game/` 目录即可使用。

## 特性

- **恒定速度**：按"像素/秒"滚动，内容越长滚得越久，视觉速度始终保持一致
- **高度自适应**：首帧自动测量内容高度，据此算出滚动时长
- **自动结束**：滚动结束后自动关闭字幕屏幕
- **淡入淡出**：显示、隐藏都带过渡效果
- **三段式内容**：图标区（图标 + 文字）、致辞、分组名单（头像 + 名字），每一段都可以留空
- **自动排版**：图标和名单每行两个，水平居中
- **可交互内容**：滚动区域里的按钮、超链接等元素可以正常点击，坐标随滚动位置换算
- **点击退出**：点击屏幕任意位置即可提前关闭
- **运行时可调**：滚动速度、开始前的停留时间都可以在脚本里随时调整

## 图片路径

组件不规定目录结构，也不要求固定的目录名：它只把 `credits_image_dir` 与图片文件名拼成完整路径，再交给 Ren'Py 按 `game/` 的搜索规则查找。脚本本身可以放在 `game/` 下的任意子目录（Ren'Py 会递归加载），图片放在哪里都可以，只要配置和实际位置对得上：

| 图片实际位置 | `credits_image_dir` 写法 |
| --- | --- |
| `game/images/credits/` | `"images/credits/"`（默认值） |
| `game/assets/staff/` | `"assets/staff/"` |
| `game/` 根目录 | `""` |

路径相对 `game/` 目录，结尾记得带 `/`。

## 安装

1. 把 `scrolling_credits_auto.rpy` 放进游戏的 `game/` 目录（或其下的任意子目录）；
2. 把图片素材放到任意位置，并把 `credits_image_dir` 指向它（见上一节）。

## 快速开始

### 第一步：填写内容

打开 `scrolling_credits_auto.rpy`，找到 `init python:` 配置块，按下面的格式填写：

```renpy
init python:
    # 图片目录：相对 game/ 目录，可自由指定（结尾要带 /）
    credits_image_dir = "images/credits/"

    # 致辞：每个字符串显示为一行，自上而下依次出现；不需要就写成空元组 ()
    credits_message = (
        "感谢游玩",
        "我们下个故事再见",
    )

    # 背景图：(image 名, 图片文件名)
    credits_background = ("credits_bg", "bg.png")

    # 图标区：(image 名, 显示文字, 图片文件名)，每行显示两个；不需要就写成 []
    credits_logos = [
        ("studio", "某某工作室", "p.png"),
    ]

    # 名单：每份名单由若干 (image 名, 显示的名字, 图片文件名) 组成，每行显示两个
    credits_members1 = [
        ("p1", "张三", "1.jpg"),
        ("p2", "李四", "2.png"),
    ]

    credits_members2 = [
        ("p3", "王五", "1.jpg"),
    ]

    # 分组标题 + 名单，显示顺序由这里决定；没有登记在这里的分组不会显示
    credits_sections = [
        ("企划：", credits_members1),
        ("程序：", credits_members2),
    ]
```

文件中预置的 `credits_members1` ~ `credits_members5` 只是示例：名单变量的数量、名称都可以随意增删或改名，只要在 `credits_sections` 里登记即可。

### 第二步：显示字幕

```renpy
# 方式一：按钮触发
textbutton _("制作名单") action Show("scroll_list")

# 方式二：在脚本里直接显示
show screen scroll_list
```

字幕显示后会自动向上滚动；点击屏幕任意位置可以提前关闭，滚动结束时也会自动关闭。

## 配置项说明

所有配置都写在 `init python:` 块里：

| 变量 | 格式 | 说明 |
| --- | --- | --- |
| `credits_image_dir` | 字符串 | 图片目录，默认 `"images/credits/"`，相对 `game/` 目录，可自由指定 |
| `credits_message` | 元组，每项一个字符串 | 致辞文本，每项显示为一行；空元组表示不显示 |
| `credits_background` | `(image 名, 图片文件名)` | 背景图，按整屏 `cover` 方式显示 |
| `credits_logos` | 列表，每项 `(image 名, 显示文字, 图片文件名)` | 图标区，文字在上、图片在下，每行两个；空列表表示不显示 |
| `credits_membersN` | 列表，每项 `(image 名, 显示名字, 图片文件名)` | 一份名单，头像在上、名字在下，每行两个 |
| `credits_sections` | 列表，每项 `(分组标题, 名单列表)` | 分组标题与顺序；成员为空的分组自动跳过 |

关于 `(image 名, 显示文字, 图片文件名)` 形式的条目：

- 第一个字段是 Ren'Py 的 **image 名**，组件会自动把它注册成图片（背景、图标、头像都是如此），屏幕里直接 `add` 这个图片名；
- 第二个字段是**显示给玩家看的文字**；
- 第三个字段是**图片文件名**，与 `credits_image_dir` 拼接后即为素材路径。

同一个 image 名只会注册一次：如果有两条内容用了相同的名字，会复用第一次注册的图片；也建议不要与项目里已有的图片重名。

## 调整滚动

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `scroll_speed` | `160.0` | 滚动速度，单位：像素/秒 |
| `scroll_hold` | `0.0` | 开始滚动前的停留时间，单位：秒（`0` 表示立即开始） |
| `fadein_time` | `0.3` | 画面淡入时间，单位：秒 |
| `fadeout_time` | `0.5` | 画面淡出时间，单位：秒 |

滚动时长由内容高度决定：

```
滚动路程 = 屏幕高度 + 内容高度
滚动时长 = 滚动路程 ÷ 滚动速度 + scroll_hold
```

例如 1080p 屏幕、内容高 3000 像素、速度 160 像素/秒时，滚动约 (1080 + 3000) ÷ 160 ≈ 25.5 秒。

`scroll_speed` 和 `scroll_hold` 是 `default` 变量，除了直接修改默认值，也可以在显示屏幕之前临时调整：

```renpy
$ scroll_speed = 240.0
$ scroll_hold = 1.0
show screen scroll_list
```

（这两个值在显示 `scroll_list` 时读取，显示前设置即可生效。）

## 自定义外观

样式与 transform 都集中在文件中部，按需修改即可：

| 名称 | 作用 |
| --- | --- |
| `style credits_text` | 所有文本的基础样式（字体、字号、颜色、对齐方式） |
| `style credits_title` | 图标区文字，53 号字、蓝色描边 |
| `style credits_subtitle` | 分组标题，40 号字、蓝色描边 |
| `style credits_say` | 致辞文本，36 号字 |
| `style credits_vbox` | 内容整体的纵向间距，默认 20 |
| `style credits_hbox` | 每行两列的水平间距（默认 150）与居中方式 |
| `transform credits_avatar` | 头像尺寸，默认 150×150、`fit "contain"` |
| `transform credits_logo_image` | 图标尺寸，默认 400×400、`fit "contain"` |
| `transform credits_bg_image` | 背景图，默认铺满整屏、`fit "cover"` |
| `transform credits_fade` | 显示 / 隐藏时的淡入淡出 |

## 工作原理

内容从"顶边贴着屏幕底边"开始，滚到"底边离开屏幕顶边"为止：

```
滚动路程 = 屏幕高度 + 内容高度
```

`ScrollCredits` 是一个自定义 `Transform`：

1. 首帧渲染时量出内容的真实高度，按速度算出总时长；
2. 之后每帧按已流逝时间计算偏移，把内容画到对应的 y 位置；
3. 鼠标、键盘事件按同样的偏移换算坐标后转发给内容，保证可交互元素点得准；
4. 滚动结束时关闭字幕屏幕。

## 注意事项

- 背景图是必须的（屏幕会直接显示 `credits_background[0]`），图标、致辞、名单都可以留空。
- 图片目录不固定，由 `credits_image_dir` 决定；目录或文件名写错时，Ren'Py 会提示找不到图片。
- 头像、图标、背景的尺寸都在 transform 里统一控制，改一处即可全局生效。
- 每次显示 `scroll_list`，滚动都会从头开始。
- 组件内的配置项、样式与 transform 统一使用 `credits_` 前缀；滚动参数沿用 `scroll_*` 命名。如与项目现有命名冲突，直接改名即可。
