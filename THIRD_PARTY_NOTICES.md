# 第三方来源说明

本项目当前集成或参考了以下开源项目。此文件只记录来源与当前取得版本，不替代上游许可证文本。

## Numerologist Skills — 紫微斗数

- 来源：<https://github.com/FANzR-arch/Numerologist_skills>
- 集成位置：`vendor/Numerologist_skills`
- 当前取得提交：`ea28c3f`
- 用途：紫微斗数三合派排盘口径、安星表、四化表、格局规则与紫微星位置校验参考。
- 实现说明：上游仅提供规则资料和单项校验脚本；玄衡的十二宫全盘、辅煞、四化、大限、结构检测与缓存接口由本项目重新实现。
- 许可说明：当前取得版本未发现根目录或紫微目录的独立 `LICENSE` 文件。正式公开发布前必须向上游确认复用许可；在许可明确前不得把上游原文作为产品内容大段公开分发。

## Tarot Skill

- 来源：<https://github.com/daman-ovo-0404/tarot-skill>
- 集成位置：`vendor/tarot-skill`
- 当前取得提交：`a9f59f0`
- 用途：塔罗牌组、牌阵定义、抽牌逻辑与解读资料的后端基础。
- 许可说明：上游 README 标注为 MIT；当前取得版本未包含单独的 `LICENSE` 文件，正式对外发布前仍需向上游确认或补齐许可文件。

## Mystic Draw

- 来源：<https://github.com/datturbomoon/Mystic-Draw>
- 用途：仅参考“先显示牌背、逐张翻牌、全部揭示后出现解读”的交互节奏；未复制其代码或图像资产。
- 上游许可：MIT。其 README 标注牌面图像来源为 CC0；玄衡当前版本未使用这些图像。
