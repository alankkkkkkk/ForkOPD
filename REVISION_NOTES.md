# ForkOPD 修订说明（对应审稿意见）

本文件逐条说明对 `main.tex` 的修改、修改理由，以及**需要作者对照真实实现/日志核实的地方**。
修订后正文（至 Conclusion）仍在 8 页内结束，Limitations 从第 9 页开始（ACL 允许）。本地用 TeX Live 2023 编译；原始源码在同一环境下编译出的行号与仓库中原 PDF 完全一致，因此版面判断可靠。仓库中的 PDF 已用修订后源码重新生成。

---

## 1.【必须修】λ∈[0,1] 的约束与无约束最优解不一致 —— 意见成立，已修

核对：反例 b=0.5、等权、f=(0.2,0.8)、V=(0.8,0.2) 得 A=D=0.18ω、C=−0.18ω、λ_u*=−1、η=1，而受约束最优 λ_c*=0，S(λ_c*)=S(0)。另随机检验了 η_c 的两种表达式与 clip 最优性（数值验证通过）。

修改：
- **Proposition 1**：引入 A、C、D（ω 加权和），写出 S(λ)=D−2λC+λ²A；同时给出 λ_u*=C/A（ℝ 上最优）与 λ_c*=clip(C/A,0,1)（[0,1] 上最优），以及 A=0 时 S≡D、取 λ_c*=0 的退化情形；"式(6)分子对 C 无偏"。
- **Theorem 2**：同时给出 η=C²/(AD)（无约束）与 η_c=(2λ_c*C−(λ_c*)²A)/D（受约束），并说明 0≤η_c≤η≤1、η_c=η 当且仅当 λ_u*∈[0,1]；A=0 或 D=0 时无可节省，记 η=η_c=0。
- **附录 A 证明**：配方 S(λ)=S(λ_u*)+A(λ−λ_u*)²，得到第二种形式 η_c=η−(C−λ_c*A)²/(AD)；证明 η_c≥0、η_c≤η、η_c=0 ⇔ C≤0；处理 A=0、D=0。新增"Example: η_c<η"段落给出审稿人的反例和 C>A（斜率>1）的情形。
- **§3.5 Trust coefficient**：区分 λ_u* 与 λ_c*；式(6)后"clip 到 [0,1]"保留。
- **Theorem 2 之后**：改为"在 λ_c* 处方差不超过 forks alone"（0 可行，所以成立）；"反相关预测器 η>0 但 η_c=0"；1/n 超额结论限定在 λ_u*∈[0,1] 时成立；附录补充 clip 是投影、非扩张。
- **在线 η̂（附录 A "Estimating η_c"）**：改为受约束版本的 plug-in：η̂=(2λ̂Ĉ−λ̂²A)/Ŝ_0，λ̂=clip(Ĉ/A,0,1)。当 0≤Ĉ≤A（clip 不生效）时它与原来的 λ̂²A/Ŝ_0 完全相同；Ĉ≤0 时为 0。同时说明它是比值估计、不是无偏的。
- 图 3 标题、§3.2、§3.5 中 η̂ 的说法同步改为"η_c 的估计"。

## 2.【必须改措辞】η 不是总方差节省比例 —— 意见成立，已改

- 摘要："the variance that hindsight saves equals a weighted squared correlation" → "estimates online the share of predictor-dependent variance that hindsight removes"。
- 引言、贡献点、§3.2（"removable variance share η"）、§3.5（"variance share η_c removed by the clipped coefficient"）、§4.4 梯度质量段（"S(0) is 58% of the variance of forks alone, and hindsight can remove η=0.23 of it, about 13% of the total"）统一为"预测器相关方差分量 S(·) 中可去除的比例"。0.58×0.23≈13% 的总量结论保持不变。

## 3.【必须修】M=1 消融与 σ̂²=Ŷ(1−Ŷ)/(M−1) 不兼容 —— 意见成立，已补充

- 附录 B "Calibrator and residual model"：M=1 时 σ̂² 分母为 0，**改为让 h_ψ 直接拟合总残差平方 (Ŷ_k−m_k)²**（其条件期望 σ_k²+(V_k−m_k)² 正是 p_k* 需要的量），并令 u_k=√h_ψ(z_k)；说明这只改变 fork 概率，Lemma 1/Theorem 1 不受影响。
- 附录 A "Estimating η_c"：说明单次 Bernoulli 观测只能无偏估计 V 的线性函数，σ_k²=V(1−V) 和 (V−b)² 都不可无偏估计，所以 **M=1 不报告 η̂**；校正值与 λ̂ 只需 E[Ŷ|G]=V，不受影响。
- 表 3：`M=1, B=2` 行加 ‡ 脚注指向附录 B。

> ⚠️ **需核实**：以上是"最自然、可证明正确"的处理方式，但论文必须描述**真实代码**做了什么。如果你们的实现用了别的替代（例如用 f_k(1−f_k) 代替 σ̂²，或关掉 h_ψ 用均匀分配），请相应改写附录 B 该段与表 3 脚注 ‡。

## 4.【需明确】式(3)不是严格满足预算的最优分配 —— 意见成立，已改

- §3.4：式(3) 前的 B 仍称 per-response budget；式后新增"Equation (3) clips without renormalizing, so B is nominal and the p_k need not sum to it; budgets count realized forks"。
- 附录 A 新增 "Equation (3) versus p_k*" 段：
  - 最优解写成 p_k*=min{1, τ√E[Δ_k²]}，τ 由约束确定（原证明"超过 1 的固定、其余重新归一化"与此一致）；
  - 式(3) 是 plug-in 近似，cap 与 floor 在按 B/Σu 缩放后直接施加，不重新求解尺度，因此 Σp_k≠B；给出审稿人的 (0.99,0.01)→(0.99,0.025)、和为 1.015 的例子；
  - 内部边界数超过 B/p_min（本设置下 40）时，floor 本身就超出预算，式(3) 保留 floor、花费超过 B；
  - 指出严格版本可二分求 τ 使 Σclip(τu_k,p_min,1)=B（可行条件 (K−1)p_min≤B≤K−1），**但未声称做过该实验**；
  - 强调无偏性只要求 p_k>0 且 G-可测，因此不受影响；预算统计按实际 fork 数（1.06 次/回答本来就体现了这一点）。
- 附录 B 算法框中 B 改为 "nominal budget"，并注明 λ̂ clip 到 [0,1]。
- 为避免与新引入的 D 冲突，附录中原 D_k=Ŷ_k−m_k 改记为 Δ_k。

## 5.【需收窄】"错误教师不会改变期望更新" —— 意见成立，已改

- 摘要："Its step values are conditionally unbiased for any predictor, as is the unclipped gradient estimate at the sampling policy"。
- 引言："a stale or misleading teacher adds variance but no bias, and the unclipped policy-gradient estimate is unbiased at the sampling policy"（删去 "cannot tilt the expected update"）。
- §4.4："By Lemma 1, a bad predictor adds variance but no bias to Ṽ_k"（原 "costs variance only"）。
- 结论："removes its bias from the step values"（原 "removes its errors in expectation"）。
- Limitations：明确保证针对 θ_old 处的未裁剪估计量 ĝ；DAPO 裁剪+token 归一化的 surrogate 只在 θ_old 处且在归一化常数意义下与 ĝ 一致，因此**不声称**教师不能影响裁剪训练的期望更新。
- 式(5) 的 ΣÂ_k=R−b：正文改为"segment credits sum to the RLOO advantage"，并说明按 token 求和时每个 Â_k 以段长 |a_k| 加权；附录 B 新增 "Token-level credit" 段，说明 token 级总和为 Σ|a_k|Â_k ≠ R−b，且**不按段长归一化**，因为当前逐 token 复制正是 Theorem 1 的 ĝ，归一化会改变估计量。

## 6. VinePPO 预算记账 —— 字面读法下意见成立，已改为明确口径

核对：若 16.3 是"每个 VinePPO prompt"的完整回答当量，则 500×36×16.3×8192≈2.40×10⁹ < 3.9×10⁹，确实矛盾。
但论文自身的数字在另一种读法下是自洽的：
- ForkOPD：8×(1+1.06×2×0.45)=15.63，与"每 prompt 15.6"吻合（128 prompts/step）；
- VinePPO：若 16.3 是"每步生成量 ÷ 128（DAPO 一步的 prompt 数）"，则每个 VinePPO prompt ≈128×16.3/36≈58 个回答当量（每个回答 ≈7.2，对应约 12.2 个内部边界、每个续写约半个回答），36×58≈128×16.3；
- 总量：3.9×10⁹/(500×128×16)≈3.8K token，即平均回答长度约 3.8K（与 4B: 440 步/3.4×10⁹、Olmo: 400 步/3.1×10⁹ 推出的 ≈3.78K 一致），远低于 8192 上限。

修改：
- 附录 C 重写：明确单位是"平均长度的完整回答"，并按 128（DAPO 一步的 prompt 数）归一化；给出 ForkOPD 与 VinePPO 的逐项算式，以及 DAPO/VinePPO 的总量换算。
- §4.1："We match total generated tokens" → "We match generation per step, counting every continuation"；"Every 9B run generates 3.9×10⁹ tokens" → "A 9B run generates about 3.9×10⁹ tokens in 500 steps"；表 1 标题加 "about"。

> ⚠️ **需核实**：
> 1. 16.0/15.6/16.3/16.2/16.1 是否确实是"每步生成量/128"的口径；约 3.8K 的平均长度是由论文数字反推的，请用日志确认。
> 2. **审稿人未提但相关的问题**：OPSD 的平均回答长度从 3.9K 降到 1.6K（§4.2）。若各方法都跑 500 步、按每步回答当量匹配，OPSD 的总 token 会明显低于 3.9×10⁹。请确认 OPSD 是否另外延长了步数以匹配 token；否则应说明预算是按"样本数/回答当量"匹配的，并修改表 1 标题中 "per method" 的表述。

## 7. "三种模型对十个基线"超出展示范围 —— 意见成立，已改

- 摘要："over the strongest baseline (ten on Qwen3.5-9B, six on the others)"。
- 引言："against ten baselines on the 9B model and six on the others"；贡献点："against ten baselines on Qwen3.5-9B and six on two other models"。
- §4.1："We group ten baselines, all run on Qwen3.5-9B and six on the other models (Table 2)"。
- §4.2："On Qwen3.5-4B and Olmo-3-7B (six baselines, Table 2), ForkOPD again leads"（原 "The ordering holds"，Olmo 上 RLSD 与 DAPO 的次序其实对调了）。
- 表 2 标题加 "(six baselines)"（该表右半部分的编程与 GPQA 结果同样只有六个基线）。

---

## 为满足 8 页限制所做的非实质性压缩

新增内容约占 40 行，为保持正文在 8 页内，做了以下不改变科学内容的调整：
- §3.6 末尾"Gated credit … does not shrink with more samples"一句与 §4.4 梯度质量段重复，删去，并在 §4.4 加指向附录 A（gating）的引用；
- §4.1 实现细节中 "Forks restart from re-fed text … (6% extra rollout time)" 移到附录 B "Recurrent state" 段（6% 数字保留）；
- 若干措辞压缩：如 "a control uses the same model without c" → "a control omits c"；"verified test cases" → "verified tests"；"(fewer for the smaller budgets of the other models)" → "(fewer for the other models)"；表 3 标题 "gray numbers give the change from the full method" → "gray: change from the full method"。

## 其他建议核对的点

- 图 3b 与 §3.2 中的 oracle η 现在明确是**无约束** η（平方相关，即可去除比例的上界）；若某些 checkpoint 上 oracle 斜率 >1，真正可去除的是 η_c<η。正文已用 "can remove"/"removable" 表述，不需要改数字，但如果日志里方便，建议同时报告 η_c。
- §4.4 "What η̂ records" 将 η̂（η_c 的估计）与 oracle η 对比。λ̂ 在 0.81–0.94 之间时二者的 plug-in 一致；如果这个范围是平滑后的均值，请确认单批次 λ̂ 是否偶有被 clip 到 1 的情况。若有，图 3b、表 5 最后一行及消融中的 η̂ 数值需用新公式重算（clip 不生效的批次数值不变）。
- 附录中 "η̂=0 when A=0 or Ŝ_0≤0" 与 "λ̂=0 if A=0" 是我补充的退化约定，请与代码对齐。
