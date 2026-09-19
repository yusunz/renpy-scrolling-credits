default scroll_speed = 160.0   # 滚动速度
default scroll_hold = 0.0      # 开始滚动前停留的秒数
define fadeout_time = 0.5         # 画面淡出时间（秒）
define fadein_time = 0.3          # 画面淡入时间（秒）

# 通用滚动字幕组件
# 仓库：https://github.com/yusunz/renpy-scrolling-credits
#
# 使用方法：
#   1) textbutton _("A") action Show("scroll_list")
#   2) show screen scroll_list

# 显示 / 隐藏时的淡入淡出
transform credits_fade:
    on hide:
        alpha 1.0
        linear fadeout_time alpha 0.0
    on show:
        alpha 0.0
        linear fadein_time alpha 1.0

# 头像：统一 150×150，等比缩放
transform credits_avatar:
    xalign 0.5
    xysize (150, 150)
    fit "contain"

# 图标：统一 400×400，等比缩放
transform credits_logo_image:
    xalign 0.5
    xysize (400, 400)
    fit "contain"

# 背景：铺满整个屏幕
transform credits_bg_image:
    xysize (config.screen_width, config.screen_height)
    fit "cover"

init python:
    # 图片目录：相对 game/ 目录，可自由指定（结尾要带 /）
    # 组件把“目录 + 文件名”拼成完整路径，再交给 Ren'Py 查找
    credits_image_dir = "images/credits/"

    # 致辞：每个字符串显示为一行，自上而下依次出现；不需要就写成 ()
    credits_message = ("************", "**************")

    # 背景图：(image 名, 图片文件名)
    credits_background = ("CCC", "bg.png")

    # 图标区：(image 名, 显示文字, 图片文件名)
    credits_logos = [
        ("project", "displayNAME", "p.png"),
    ]

    # 名单 1：(image 名, 显示名字, 图片文件名)
    credits_members1 = [
        ("name1", "displayname1", "1.jpg"),
        ("name2", "displayname2", "2.png"),
    ]

    # 名单 2
    credits_members2 = [
        ("name1", "displayname1", "1.jpg"),
        ("name2", "displayname2", "2.png"),
    ]

    # 名单 3
    credits_members3 = [
        ("name1", "displayname1", "1.jpg"),
        ("name2", "displayname2", "2.png"),
    ]

    # 名单 4
    credits_members4 = [
        ("name1", "displayname1", "1.jpg"),
        ("name2", "displayname2", "2.png"),
    ]

    # 名单 5
    credits_members5 = [
        ("name1", "displayname1", "1.jpg"),
        ("name2", "displayname2", "2.png"),
    ]

    # 分组标题 + 名单：显示顺序由这里决定，新增名单必须在这里注册
    credits_sections = [
        ("职责1：", credits_members1),
        ("职责2：", credits_members2),
        ("职责3：", credits_members3),
        ("职责4：", credits_members4),
        ("职责5：", credits_members5),
    ]

    # 记录已注册的 image 名，避免重复注册
    credits_registered_images = set()

    # 注册背景
    image_name, image_file = credits_background
    if image_name not in credits_registered_images:
        renpy.image(image_name, At(credits_image_dir + image_file, credits_bg_image))
        credits_registered_images.add(image_name)

    # 注册图标
    for image_name, display_name, image_file in credits_logos:
        if image_name not in credits_registered_images:
            renpy.image(image_name, At(credits_image_dir + image_file, credits_logo_image))
            credits_registered_images.add(image_name)

    # 注册所有头像
    for section_title, members in credits_sections:
        for image_name, display_name, image_file in members:
            if image_name not in credits_registered_images:
                renpy.image(image_name, At(credits_image_dir + image_file, credits_avatar))
                credits_registered_images.add(image_name)

# =====================================================================
#  自适应滚动字幕
#
#  原理：
#     滚动长度 = 屏幕高度 + 内容高度
#     滚动时间 = 长度 ÷ 速度        （内容越高 → 时间越长，速度恒定）
#     ScrollCredits 在首帧渲染时量出内容高度，算出滚动时长；
#     滚完那一刻直接隐藏画面。
#
#  ▸ 想调速：改下面 scroll_speed 的数值（单位：像素/秒）
#  ▸ 想让开头停一下再滚：改 scroll_hold（秒，0 表示立刻滚）
# =====================================================================

init python:
    class ScrollCredits(Transform):
        """
        让内容以【恒定速度】从屏幕底部向上滚动。

        核心公式：
            内容从“顶边贴在屏幕底部”滚到“完全滚出屏幕顶部”，
            移动总像素 = 屏幕高度 + 内容高度

            滚动时长 = 移动总像素 ÷ 速度

        render() 会被引擎每帧调用一次：
            · 第一帧：渲染一次子内容（screen 里的 frame），
            量出内容高度，据此算出滚动时长；
            · 之后每帧：按已过时间算进度，把内容画在对应的 y 位置；
            · 滚完那一刻：直接隐藏字幕画面。
        """

        def __init__(self, speed=160.0, hold=0.0):
            super().__init__()              # child 稍后由 __call__ 挂上
            self.speed = float(speed)       # 像素/秒
            self.hold = float(hold)         # 开始前停留秒数
            self.content_h = None           # 内容高度（首帧量出后缓存）
            self.duration = None            # 滚动动画时长
            self.first_st = None            # 首帧的时间戳
            self.finished = False           # 是否滚完

        def __call__(self, child=None, take_state=True, _args=None):
            # Ren'Py 的 screen 里 `at 某个transform` 会被引擎用
            # transform(child=显示对象) 再调用一次。基类 __call__ 会返回
            # 普通 Transform 丢掉子类，所以这里重新构造并挂上内容。
            rv = self.__class__(
                speed=getattr(renpy.store, "scroll_speed", self.speed),
                hold=getattr(renpy.store, "scroll_hold", self.hold),
            )
            if child is not None:
                rv.set_child(child)
            return rv

        def render(self, width, height, st, at):
            if self.child is None:
                return super().render(width, height, st, at)

            # 1) 渲染子内容（frame 里的整个 vbox），量出它的真实尺寸
            child_render = renpy.render(self.child, width, height, st, at)
            cw, ch = child_render.get_size()

            if self.content_h is None:
                # 第一帧：长度 = 屏幕高 + 内容高；时长 = 长度 ÷ 速度
                self.content_h = ch
                self.first_st = st
                self.duration = (renpy.config.screen_height + ch) / self.speed + self.hold

            # 2) 算当前进度（0=最底部，1=完全滚出）
            t = (st - self.first_st) - self.hold
            t = max(0.0, t)
            progress = min(1.0, t / self.duration) if self.duration else 1.0

            if progress >= 1.0 and not self.finished:
                self.finished = True
                # 滚完了：直接隐藏字幕画面（下一帧生效）
                renpy.hide_screen("scroll_list")
                renpy.restart_interaction()

            # 3) 内容顶边此刻的 y 坐标（像素）
            #    进度0：y = 屏幕高（内容整块在屏幕下方）
            #    进度1：y = -内容高（内容整块滚出屏幕上方）
            sh = renpy.config.screen_height
            y = sh - progress * (sh + self.content_h)
            # 记录当前滚动偏移，供 event() 换算事件坐标
            self.current_y = y

            # 4) 合成到一块“屏幕大小”的画布上
            rv = renpy.Render(int(cw), int(sh))
            rv.blit(child_render, (0, int(round(y))))

            # 5) 没滚完就继续刷新。
            #    redraw 的 when=0 表示“尽快重绘”，即每帧都重绘，
            #    帧率交给引擎调度（引擎自己的动画显示对象也是这么写的），
            #    这样无论显示器是 60/120/144Hz 都能跑满。
            if not self.finished:
                renpy.redraw(self, 0)

            return rv

        def event(self, ev, x, y, st):
            # 把鼠标/键盘事件转发给滚动内容，坐标减去滚动偏移，
            # 否则内容里的超链接等可交互元素收不到点击。
            if self.child is None:
                return None
            return self.child.event(ev, x, y - getattr(self, "current_y", 0), st)

    # 固定一个 transform 模板实例。screen 的 at 引用它，保证跨帧复用
    # 同一个对象（若每次现建，滚动进度会被清零）。
    scroll_credits_tf = ScrollCredits()

# =====================================================================
#  样式
# =====================================================================

style credits_text:
    font gui.text_font
    color "#ffffff"
    size 28
    xalign 0.5

style credits_title is credits_text:
    outlines [(1, "#4da6ff", 0, 0)]
    size 53

style credits_subtitle is credits_text:
    outlines [(1, "#4da6ff", 0, 0)]
    size 40

style credits_say is credits_text:
    size 36

style credits_vbox:
    spacing 20

style credits_hbox:
    xalign 0.5
    spacing 150


# =====================================================================
#  字幕屏幕
# =====================================================================

screen scroll_list():
    button:
        xfill True
        yfill True
        background None
        action Hide()
    add Solid("#000000") at credits_fade
    add credits_background[0] at credits_fade
    # 黑色透明遮罩
    # add Transform(Solid("#000000"), alpha=0.25) at credits_fade

    frame:
        xfill True
        at [scroll_credits_tf, credits_fade]
        background None
        vbox style "credits_vbox":
            xfill True
            xalign 0.5
            style_prefix "credits"

            if credits_logos:
                for i in range(0, len(credits_logos), 2):
                    $ image_name, display_name, image_file = credits_logos[i]
                    hbox style "credits_hbox":
                        spacing 50
                        vbox:
                            text display_name style "credits_title"
                            add image_name
                        if i + 1 < len(credits_logos):
                            $ image_name, display_name, image_file = credits_logos[i + 1]
                            vbox:
                                text display_name style "credits_title"
                                add image_name

            if credits_message:
                for line in credits_message:
                    text line style "credits_say"

            for section_title, members in credits_sections:
                if members:
                    text section_title style "credits_subtitle"
                    for i in range(0, len(members), 2):
                        $ image_name, display_name, image_file = members[i]
                        hbox style "credits_hbox":
                            vbox:
                                add image_name
                                text display_name
                            if i + 1 < len(members):
                                $ image_name, display_name, image_file = members[i + 1]
                                vbox:
                                    add image_name
                                    text display_name
