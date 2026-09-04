# 玄衡项目记忆索引

> 这是项目记忆的唯一入口，不再承载完整历史。上下文压缩、新会话或继续任务时，先完整阅读本文件，再按“读取路由”只读取与当前任务直接相关的记忆。禁止一次性加载全部分册。

## 1. 当前快照

- 产品：玄衡；四柱八字、塔罗占问、紫微斗数、合缘共用出生档案与“玄夜星图”视觉系统。
- 阶段：V1 八字、V2 塔罗、V3.2 紫微与 V4 合缘均为本地 RC；紫微功能闭环已完成但排盘仍待 30 盘校准。
- 当前工作：进行 V1/V2/V3/V4 联合人工验收，以及紫微 30 盘校准与闰月口径确认。
- 尚未开始：正式上线、云端持久化、账户/跨设备同步、上线后 D 类验收。
- 最新功能基线：当前 `main` 分支最新提交；具体提交号从 Git 历史读取，不在正文循环追写。
- 本地入口：双击 `打开玄衡.command`，并保持服务终端运行；直接打开 `index.html` 不能使用后端功能。
- 当前待验收项的唯一来源：[ACCEPTANCE_CHECKLIST.md](ACCEPTANCE_CHECKLIST.md)。代码完成或自动测试通过，不等于用户验收通过。

## 2. 读取路由

只读取完成当前任务所需的最少文件；跨领域任务可组合读取，但不要预读无关分册。

| 当前任务 | 必读记忆 | 何时追加读取 |
| --- | --- | --- |
| 产品范围、命名、交互原则、数据边界 | [01-product-decisions.md](project-memory/01-product-decisions.md) | 涉及具体版本时再读 `03-versions.md` |
| 后端、数据库、接口、本地服务、缓存、故障排查 | [02-architecture-runtime.md](project-memory/02-architecture-runtime.md) | 涉及上线时再读 `05-release-risks.md` |
| V1/V2/V3/V4 功能开发或范围判断 | [03-versions.md](project-memory/03-versions.md) | 开始验收时再读 `ACCEPTANCE_CHECKLIST.md` |
| 前端、样式、布局、组件、响应式、视觉回归 | [04-visual-system.md](project-memory/04-visual-system.md) | 验收视觉时再读 `ACCEPTANCE_CHECKLIST.md` |
| 部署、GitHub、云端数据、密钥、许可证 | [05-release-risks.md](project-memory/05-release-risks.md) | 需要技术现状时再读 `02-architecture-runtime.md` |
| 用户验收、待验收项、固定样例 | [ACCEPTANCE_CHECKLIST.md](ACCEPTANCE_CHECKLIST.md) | 只在需要追溯原因时读 `90-milestones.md` |
| 追溯某次改动、历史原因、回归来源 | [90-milestones.md](project-memory/90-milestones.md) | 不作为日常任务默认上下文 |
| 第三方来源与许可证明细 | [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) | 发布或更新上游依赖时读取 |

## 3. 当前推进顺序

1. 人工验收最新视觉统一：四柱命盘/岁运/解读、问事历史侧栏、出生档案弹窗、四体系顶栏对齐。
2. 联合验收 V1 + V2：八字完整字段、问事历史/导出、塔罗牌阵/翻牌/解读/历史。
3. 验收 V4 合缘：双档案、交换、三种场景、证据、历史与导出。
4. 验收 V3.2 紫微完整闭环；随后完成至少 30 盘校对与闰月口径决策。
5. 完成全站视觉收尾与多设备回归。
6. 建立正式线上工程、数据库、服务端密钥与 D 类验收。

## 4. 记忆维护规则

- 根文件目标控制在 100 行以内，只保存“现在是什么、正在做什么、下一步是什么、去哪里找”。
- 产品决策只写入 `01-product-decisions.md`；工程事实只写入 `02-architecture-runtime.md`；版本范围只写入 `03-versions.md`；视觉规范只写入 `04-visual-system.md`；发布风险只写入 `05-release-risks.md`。
- 完成里程碑时：先更新对应分册的当前状态，再向 `90-milestones.md` 添加一条短记录；不要把过程日志复制到根文件。
- 新增或改变待验收项只更新 `ACCEPTANCE_CHECKLIST.md`；根文件只在验收阶段整体变化时更新一句当前状态。
- 使用统一状态词：`计划中`、`已实现`、`自动测试通过`、`待人工验收`、`人工验收通过`、`已发布`。不得把相邻状态互相代替。
- 发生决策推翻时，在对应分册直接更新有效结论，并在里程碑中记录“旧决定 → 新决定”；不在多个文件保留互相冲突的现行说法。
- 不记录 API Key、姓名、出生日期、地点、经纬度、问题正文或其他用户敏感数据。

## 5. 跨上下文恢复方法

1. 读本文件，确认当前阶段和任务领域。
2. 按读取路由打开 1 个主要分册；确有跨域依赖时再增加 1—2 个。
3. 需要判断“是否已经验收”时，以 `ACCEPTANCE_CHECKLIST.md` 为准；需要判断“为何这样做”时，才查 `90-milestones.md`。
4. 再检查相关代码和最新 Git 状态，不用历史叙述替代当前代码事实。
