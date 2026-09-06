# 考公 AI Skills

**把公开课中有依据的解题方法，变成可以反复使用的 AI 考公学习技能。**

考公 AI Skills 是一个免费分享的学习项目：从 B站、YouTube 等平台搜集中国大陆考公公开课，将实际读取到的教学信息整理为 AI 可以调用的讲题流程、训练方法和来源索引。覆盖行测、申论、结构化面试，兼顾知名讲师、机构账号与较低曝光的个人创作者。

你可以用它让 AI 讲清一道题的适用方法和易错点，把申论答案逐项对应到材料，进行结构化面试练习，也可以继续加入新的公开课材料。每条方法保留来源和适用边界，方便回看原作者内容；整理者补充的检查步骤与原创练习会单独标明。

**版本：0.1.0，研究日期：2026-09-06。当前是可用的首轮研究版，完整字幕读取为0、完整课程观看为0。** 共登记51个来源，其中B站视频28个、YouTube视频18个；实际抽样读取5个YouTube视频画面，另读取公开简介、图文和官方文件。不能将46个视频入口说成46门课程精读。

## 可以直接使用什么

| 内容 | 用途 |
|---|---|
| [kaogong-coach](skills/kaogong-coach/SKILL.md) | 行测推导与错因诊断、申论材料映射与批改、面试情境训练 |
| [kaogong-source-distiller](skills/kaogong-source-distiller/SKILL.md) | 将后续视频／字幕／作者图文转为有证据的方法卡 |
| [25张方法卡](docs/method-cards.md) | 9张有局部来源依据、14张原创设计、2张待核验候选 |
| [32张讲师／频道卡](skills/kaogong-coach/references/creators.md) | 查看已知主题、局部方法、身份关系与下一步阅读缺口 |
| [51条来源清单](docs/source-catalog.md) | 跳转原始页面，核对实际读取范围 |

32张卡按平台内身份分别登记，**不是32位已独立认证的老师，也不是32套完整个人技能**。跨平台身份未经核实不合并；低播放视频不等于冷门老师，更不等于低教学质量。

## 证据覆盖

| 阅读层级 | 来源数 | 可以说明什么 |
|---|---:|---|
| 搜索索引 `search_only` | 19 | 候选课程与有限元数据 |
| 简介／目录 `description_only` | 22 | 页面实际陈述与课程结构，不能代替整课 |
| 正文 `article_body` | 5 | 2份官方文件、1篇作者图文、2篇学习者笔记 |
| 画面抽样 `video_sample` | 5 | 已登记时间点可读的题面、公式与圈划 |
| 字幕 `transcript` | 0 | 本轮未取得 |

5个画面样本中，3个具有足够清晰的局部教学规则；另外2个只能确认批改或图推演示形式，没有虚构未看清的评语和算法。9张来源方法卡中，4张来自B站作者简介／图文，5张来自上述3个YouTube视频的局部画面。

具体例子：

- **叽叽喳喳**：依据本人公开简介，组织同年同考区不同卷的练习与难度递进。
- **永岸申倩**：依据本人公开图文，整理归纳概括的审题、找点、压缩和组织步骤。
- **公考老师-水果频道**：依据01:30课堂画面，整理主旨题中中心建议与例证的区分。
- **行测喜哥频道**：依据03:00、07:20板书，整理总分量补缺、量纲转换、均值与比重口径。

每张卡附来源、定位、边界与原创例题。项目增加的回填验证、证据矩阵等操作明确标记为整理者补充，不冒称讲师原话。详见[方法卡](docs/method-cards.md)与[研究说明](docs/research-notes.md)。

## 安装与调用

两个 skill 都是独立的 `SKILL.md + references/ + scripts/` 文件夹，无模型密钥和第三方Python依赖。将 `skills/` 下需要的技能文件夹复制到所使用 AI 代理的技能目录；不要只复制 `SKILL.md` 而漏掉引用资源。

Codex 的个人技能目录默认是 `~/.codex/skills/`；若设置了 `CODEX_HOME`，则使用其下的 `skills/`。复制前检查同名目录，保留已有内容。示例调用：

```text
使用 $kaogong-coach 讲解：现期120，同比增长20%，增长量多少？
先给精确列式，再说明为什么不能直接用120×20%。
```

```text
使用 $kaogong-coach 批改以下申论答案。
请把每个建议改动对应到给定材料；不要补造材料没有的成效。
```

```text
使用 $kaogong-source-distiller 处理我合法取得的这份字幕。
提炼讲师明确讲到的规则、适用前提、失败情况和原创练习，保留时间定位。
```

## 可运行工具

从仓库根目录执行，Python 3.10+，仅标准库：

```console
python skills/kaogong-coach/scripts/calc_check.py increment current=120 rate=20%
python skills/kaogong-coach/scripts/calc_check.py share-difference share=30% numerator_rate=20% denominator_rate=10%
python scripts/validate_catalog.py
python -m unittest discover -s tests -v
```

前两例输出精确结果20、1/40；后者是比重小数差，即2.5个百分点。负百分数建议写为 `rate=-20%`，避免命令行将它识别成选项。

字幕格式转换只处理本地输入，支持SRT、VTT、B站字幕JSON、YouTube JSON3，不负责下载或验证字幕：

```console
python skills/kaogong-source-distiller/scripts/normalize_transcript.py raw/example.vtt --output work/example.normalized.json
```

原始字幕默认留在本地，`raw/`、`work/`、`transcripts/` 及音视频文件已列入 Git 忽略规则。转换会拒绝覆盖已有输出。

## 范围和限制

当前官方基线为已核实的2026年度国考，包含政治理论在内的行测六部分；没有确认2027年度官方大纲。政治理论与常识目前只有核对来源与学习流程，未形成完整知识库。[考试范围](skills/kaogong-coach/references/exam-scope.md)记录了考季与官方出处。

本项目不承诺提分、上岸或讲师独创性，不输出伪造的官方分数。公开页面可访问不等于版权开放：仓库只收录原创摘要、链接、原创练习及代码，不重发完整课程、字幕、讲义和课堂截图。MIT许可只覆盖本项目原创内容，第三方材料权利归原权利人。

## 扩展

下一轮优先补读当前只有目录的原作者短课，获得可定位的讲解和反例后再升级方法卡。新增来源请按[证据规则](skills/kaogong-coach/references/evidence-policy.md)和[记录模板](skills/kaogong-source-distiller/references/record-template.json)登记，再运行校验。不要用新增搜索结果数量代替内容读取深度。

## 免费分享与自愿支持

本项目以**非商业的学习交流与方法整理**为目的，免费开放，不售卖原课程，也不以售卖本项目 Skills 进行商业营利。内容来自网络上搜集到的公开课及相关公开资料，仅整理实际读取到的部分；原课程、讲义及其他第三方内容的版权归原作者或相应权利人所有。

如果这些整理对你有帮助，欢迎**完全自愿地支持 5 元**，作为对资料整理、内容校验和持续维护的一点心意。支持与否均不影响免费下载和使用，也不附带额外功能、课程、服务或权益。愿意使用、提出改进建议或分享给有需要的朋友，同样是对项目的支持。谢谢你！

<p align="center">
  <a href="assets/support-qr.jpg"><img src="assets/support-qr.jpg" alt="项目维护者提供的自愿支持收款码，支持与否不影响免费使用" width="420"></a>
</p>
<p align="center">自愿支持 5 元 · 点击图片可查看原图</p>

上述非商业目的说明描述本项目维护者的运营方式，不改变 [MIT 许可](LICENSE)授予使用者的权利；MIT 仅适用于本项目原创内容，不覆盖第三方课程与素材。

发布与维护流程及本轮验证记录见[发布说明](docs/publishing.md)和[质量检查](docs/quality-checks.md)。
