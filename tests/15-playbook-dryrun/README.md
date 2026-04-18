# Playbook Dry-Run 验证（R1~R5 行为回归）

本目录不跑代码——这里是"让 AI 按 Playbook 走一遍"的人工评估证据。

## 如何使用
1. 在一个全新对话里输入对应 scenario 的需求
2. AI 应该按 Playbook 输出 `Step Rn 产出报告` 块
3. 把 AI 完整回复（所有步骤的报告 + 中间产出）贴到对应 `run_*.md`
4. 对照"预期"核对，记录偏差

## Scenario A：复现 test 14 K70 壳（全量走完 R1~R5）
**Prompt**：「帮我做一个小米 K70 的手机壳，要跟官方图片做视觉对比」
**预期产出报告数**：8 次（R1 / R2 / R2.5 / R2.7 / R3 / R3.5 / R4 / R5）
**失败判据**：
- 任一 Step 没有 `Step Rn 产出报告` 块 → 回改 Playbook 执行契约强度
- R2.7 被遗漏（最常见的 v3 问题）→ 加强 Playbook 的"FM-4"提示
- AI 直接写代码、跳过 R1/R2/R2.5/R2.7 → Playbook 入口指引不够明确

## Scenario B：有 STEP + 不做 Layer 2（走 R1/R2/R3/R3.5/R4/R5）
**Prompt**：「帮我做红米 K80 Pro 的手机壳。GrabCAD 上有 STEP，我只要模型能打印就行，不用做视觉对比」
**预期产出报告数**：**6 次**（R1 / R2 / R3 / R3.5 / R4 / R5，R2.5 + R2.7 显式 skip）
**关键检查**：
- R2 产出报告末尾必须显式声明 `[skip] R2.5 reason=已有 model.step` + `[skip] R2.7 reason=不做 Layer 2`
- R3~R5 以 STEP 为主要尺寸来源，params.md 置信度应 ≥ ★★★★
**失败判据**：
- AI 硬跑 R2.5 反推 → Playbook 分叉规则表述不清
- AI 静默 skip 不写 reason → 回改执行契约第 3 条为更严

## Scenario C：有 STEP + 要做 Layer 2（陷阱场景）
**Prompt**：「帮我做红米 K80 Pro 的手机壳。GrabCAD 上有 STEP，但我还想跟官方照片做视觉对比」
**预期产出报告数**：**7 次**（R1 / R2 / R2.7 / R3 / R3.5 / R4 / R5，只 skip R2.5）
**关键检查**：
- R2 产出报告末尾显式 `[skip] R2.5 reason=已有 model.step`，但 R2.7 必须跑
- R2.7 产出 `part_face_mapping.yaml` + 参考图 cropped/scale
- Layer 2 对比结果在 R4 报告里出现 IoU 数字
**失败判据**：
- AI 把"有 STEP"等同于"跳 R2.7" → Playbook R2.7 段"特别提示"需要加粗/重写
- Layer 2 执行失败但没按 feedback-diagnosis 回退 → 回 Playbook R4 加强

## 审阅流程
1. 跑 A/B/C 三个对话，分别粘贴到 `run_A.md` / `run_B.md` / `run_C.md`
2. 每个 run_*.md 末尾加一段"评估"：
   - 产出报告计数是否匹配预期
   - 哪一步被跳/漏
   - 需要回改 Playbook 的具体位置（行号 + 建议）
3. 所有偏差汇总到 skill 仓的 Playbook 修订 PR 里
