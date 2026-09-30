# AD — 广告拦截规则维护

## 订阅链接（推荐）

```
https://ag-jin.github.io/AD/sr_top500_whitelist_ad.conf
```

Shadowrocket → 配置 → 添加 → 粘贴上面的地址。**这个链接同时具备上游更新和自有规则**：

- 上游规则由 GitHub Actions **每天自动拉取最新版**（北京时间 06:30）
- 自有 78 条规则以标记块形式注入，**订阅更新不会冲掉**
- 构建脚本：`scripts/build-subscription.py`；工作流：`.github/workflows/build-subscription.yml`

> 用 `ag-jin.github.io` 而非 `raw.githubusercontent.com`——后者在国内被墙，会导致更新静默失败。

## 模块方案（配置切换无效时用这个）

```
https://ag-jin.github.io/AD/adblock.sgmodule
```

Shadowrocket → 底部「模块」→ 右上角 + → 粘贴地址 → 启用。

**适用场景**：设备上有多份配置（例如机场自带的配置 + 本仓库订阅），
实际生效的是另一份，更新订阅不起作用。模块叠加在**所有配置之上**，
不受配置切换影响。

模块内含 78 条 REJECT 规则，已移除指向被墙域名的 icon 引用。

## 文件

| 文件 | 说明 |
|---|---|
| `sr_top500_whitelist_ad.conf` | **订阅用**：上游规则 + 自有规则（自动构建，勿手改） |
| `adblock-ruleset.list` | RULE-SET 格式（78 条），需在配置里写一行引用 |
| `adblock-rules.conf` | 自有规则源文件（78 条），Actions 据此注入 |
| `bilibili-splash.conf` | B站开屏广告调查结论（已停用，需 MITM 才能生效，勿导入） |
| `LICENSE-CC-BY-SA-4.0.txt` | 上游规则集的许可协议 |

## ⚠️ 两个坑（都踩过，都会让规则"看起来没用"）

### 坑一：规则被订阅更新冲掉

**现象**：配置导入后能用，但过一段时间广告又回来了；配置文件大小变化（如 7.3M → 6.4M）。

**原因**：`update-url` 触发的订阅更新会**重写整个配置文件**，[Rule] 段的手写规则被上游内容覆盖。

**解法**：用本仓库的订阅链接（见顶部），它由 Actions 每天重建，自有规则以标记块注入，订阅更新后仍在。

备选：用 RULE-SET，在 `[Rule]` 段加一行 `RULE-SET,https://ag-jin.github.io/AD/adblock-ruleset.list,REJECT`（已确认 Shadowrocket 支持该指令）。

### 坑二：`raw.githubusercontent.com` 在国内被墙

**现象**：手机上从 raw 域名下载/更新配置超时失败；Shadowrocket 更新订阅时**静默失败**，界面无明确报错，配置保持原样。

**解法**：一律用 GitHub Pages 地址 `https://ag-jin.github.io/AD/...`。两者走不同 CDN，前者被墙、后者通常可直连。

**验证是否生效**：看日志里 `result` 字段。若只有早期那 20 多条规则在工作、没有 `DOMAIN-KEYWORD` 或 `DOMAIN,` 精确规则，说明新规则没进去。

> 本仓库的 `sr_top500_whitelist_ad.conf` 由 Actions 自动构建：先拉上游最新版，再注入自有规则，并把 `update-url` 指向自身，因此订阅可持续更新且不丢规则。

### 关于 `sr_top500_whitelist_ad.conf`

完整配置的构成：

- **上游订阅规则 59577 条（99.9%）** — 来自 [Johnshall/Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever)，采用 **CC BY-SA 4.0** 许可，署名与许可文件见本仓库
- **自有规则 78 条** — 位于 `[Rule]` 段顶部（第 12 行起），就是 `adblock-rules.conf` 的内容
- 无任何代理节点、UUID、密码或个人凭据，可安全公开

该文件带 `update-url`，Shadowrocket 更新订阅时会重写整个文件（含自有规则）。若需长期保留自有规则，更新后重新粘贴 `adblock-rules.conf`。

### 关于 `bilibili-splash.conf`（为什么它不能直接用）

B站开屏广告**无法用域名拦截**：广告数据来自 `app.bilibili.com/x/v2/splash/show`——这是 B站正常业务域名，广告混在它的响应 JSON 里。同一域名同时承载首页内容，封域名等于封掉整个 App。

唯一可行的拦截方式（URL Rewrite 用 `reject-dict` 返回空 JSON，或 JS 脚本删字段）**都必须 MITM 解密 HTTPS**，即需要安装并信任 CA 证书。

本仓库**不提供**依赖 MITM 的配置：若把域名写入 `[MITM]` 却未装证书，B站请求会因证书不受信任而失败——为了减少广告反而弄坏 App。该文件保留为调查结论记录。

## 用法

Shadowrocket → 配置 → 当前配置 → 编辑 → 粘贴到 `[Rule]` 段**顶部**。

> **必须放在订阅规则之前**：Shadowrocket 是先匹配者生效，订阅里的大量 `DIRECT` 白名单会抢先放行。

## 已知坑

这轮调试踩到的、值得记下来的：

1. **`DOMAIN-SUFFIX` 匹配不到连字符前缀域名**

   ```ini
   DOMAIN-SUFFIX,remad.qm989.com,REJECT      # ❌ 匹配不到 a6-remad.qm989.com
   DOMAIN-KEYWORD,remad.qm989.com,REJECT     # ✅ 正确
   ```

   `DOMAIN-SUFFIX,x` 只匹配 `x` 本身和 `*.x`。七猫的广告位叫 `a6-remad`、`t-remad`——`remad` 前面是连字符不是点，所以后缀规则是死的。

2. **不支持通配符**

   ```ini
   DOMAIN-SUFFIX,pangolin-sdk-toutiao*,REJECT   # ❌ 无效，会被静默忽略
   ```

   必须逐条列出 `.com` / `1.com` / `2.com` / `-b.com`（它们是不同集群）。

3. **拦"打包素材域"≠ 拦广告**

   `pglstatp-toutiao.com` 是广告素材包下发域，拦它有用于减少流量，但**真正拉广告的是 `api-access.pangolin-sdk-toutiao*.com`**。只拦前者会误以为已生效。

4. **订阅更新会覆盖手写规则**

   带 `update-url` 的配置每次更新会重写整个文件。自定义规则要单独存档（就是本仓库），更新后重新粘贴。

## 效果与边界

在七猫上实测有效：拦截内容接口 + 全部已知广告联盟后，广告基本消失。

**边界**（域名拦截的固有上限）：

- **IP 直连** — 日志中有 2000+ 次纯 IP 请求，无域名可匹配，`DOMAIN-*` 规则一律失效
- **广告域名轮换** — 实测半小时内穿山甲换过 `v26` → `v5-ex` → `v9` 三个素材域
- **SDK 兜底** — 拉不到填充时 App 可能显示占位或换联盟重试

因此规则需要持续跟进。发现新广告域时，用下方方法论定位并补充。

## 曾经的误判（已修正）

早期版本认为七猫的 `api-bs` / `api-gw` / `api-cfg` / `drs` 是"正文接口，拦了会白屏"，
因此没有拦截。**这个判断是错的**：

- 社区维护的[七猫专用规则库](https://github.com/5528046/AD--)把这些接口全部拦截
- 实测拦截后七猫可正常打开、翻页

现已全部加入规则。正文内容不依赖这些接口，它们主要承担广告/配置/统计下发。
```


## 与分流配置的关系（重要）

本模块**只做拦截，不参与分流**。规则全部是 `REJECT`，不含任何 `PROXY`/`DIRECT`：

```
模块职责：决定"什么该被拦"
配置职责：决定"其余的走代理还是直连"
```

两者叠加工作，互不干扰：

| 层级 | 作用 | 更新方式 |
|---|---|---|
| 模块（本项目） | 广告/追踪拦截 | 独立更新，不受配置切换影响 |
| 配置（如 johnshall 订阅） | 分流 + 基础域名黑名单 | 订阅更新会重写整个文件 |

**为什么用模块而不是改配置**：配置同时只能启用一份，且订阅更新会重写文件、冲掉手写规则。
模块叠加在所有配置之上，独立生效。

## 排错：如何确认模块已生效

模块名自带版本标记：

```
#!name=广告拦截规则 v1.6 (116条 · 2783dff5)
```

在 Shadowrocket →「模块」列表里直接看名字：

- 显示 `v1.6 (116条)` → 最新版已加载
- 显示更早版本或条数不符 → **删除后重新添加**（模块有缓存，改内容不一定会自动重下）

验证规则是否真的在拦截，用运行时日志（Shadowrocket 设置 → 诊断，或局域网 `/api/log`）查看：

```
tcp rule => {
    result = DOMAIN-SUFFIX,yingt.fun,REJECT,
    type = REJECT,
    url = orzonera.yingt.fun:443
}
```

`type = REJECT` 即为拦截成功。

## 方法论：如何定位漏点

本项目所有规则都来自真实流量日志分析，流程：

1. **抓日志** — 用运行时诊断日志（含完整 URL 路径与 UA），比 `.db` 详细
2. **找高频** — 按出现次数排序，广告/埋点通常高频（如 `yingt.fun` 124 次）
3. **验归属** — 查证书主体、NS 服务器、域名创建时间
   - 七猫正规域名用 `VIP3.ALIDNS.COM`；`yingt.fun` 用 `cwbgp.space` → 第三方服务
4. **看 UA** — 确认请求方。注意 `YYReader` 就是七猫自己（yueyou=阅友=七猫开发主体）
5. **交叉验证** — 与 anti-AD / AdRules / EasyList CN / 217heidai 四库比对
6. **社区背书** — 搜专用规则库（如 `5528046/AD--` 的小说规则库）


## 外部参考：社区七猫专用模块

**fmz200/wool_scripts** — 作者"奶思"维护的七猫去广告模块（多平台）：

- Shadowrocket: [QiMaoNovel.srmodule](https://github.com/fmz200/wool_scripts/raw/main/Shadowrocket/module/split/partQ/QiMaoNovel.srmodule)
- Surge: `Surge/module/split/partQ/QiMaoNovel.sgmodule`
- Loon: `Loon/plugin/split/partQ/QiMaoNovel.lpx`
- QuantumultX: `QuantumultX/rewrite/split/partQ/QiMaoNovel.snippet`

它的做法：**域名规则 + URL Rewrite（需 MITM）**双管齐下：

```ini
[Rule]                      # 域名层（本项目已全部覆盖）
DOMAIN,cdn-new-ad.wtzw.com,REJECT
DOMAIN,a-remad.qm989.com,REJECT
DOMAIN,qzs.gdtimg.com,REJECT

[URL Rewrite]               # 路径层（需 MITM 证书）
^https?://api-cfg\.wtzw\.com/v1/(adv|reward|operation) - reject
^https?://api-access\.pangolin-sdk-toutiao-b\.com/api/ad/union/sdk/get_ads - reject
^https?://open\.e\.kuaishou\.cn/rest/e/v3/open/univ - reject
^https?://p1-lm\.adukwai\.com/bs2/adUnionVideo - reject
^https?://lf-cdn-tos\.bytescm\.com/obj/static/ad - reject
```

**关键情报**：`URL Rewrite` 用精确路径拦截（如 `/api/ad/union/sdk/get_ads`），
这正是本项目"域名拦截"做不到的——同一域名下区分正文与广告请求。
它需要 MITM，本项目不使用证书，故仅采纳其域名部分。

**注意到**：该模块还有一条 `[MTIM]` 说明"删除了域名 lf-cdn-tos.bytescm.com，原因是无法 MITM"，
印证了路径层拦截的局限。

## 维护记录

- **2026-09-29（第五轮）** — 加入 `yingt.fun`（第三方广告/埋点：NS 非七猫自有、随机子域、高频 124 次）。广告基本消失。规则 104 → **116 条**。
  同时修正两处早期误判：① `api-bs`/`api-gw` 等被判定"拦了会白屏"而漏拦，实测可拦；② `YYReader` UA 被误判为其他 App（实为七猫，yueyou=阅友=七猫开发主体），导致 `zztfly.com` 系全部漏拦。
- **2026-09-29（第四轮）** — 采纳社区七猫专用规则库，补拦 `api-bs`/`api-gw`/`api-cfg`/`drs`/`api-sc` 等内容接口 + 快手/神马/UC/广点通联盟。规则 78 → 104 条。
- **2026-09-29（第三轮）** — 补拦 `mkt.wtzw.com` 等，规则 56 → 78 条。
- **2026-09-29（第二轮）** — 定位根因：设备订阅更新失败（`raw.githubusercontent.com` 被墙）。规则 34 → 56 条。
- **2026-09-28（初版）** — 基于三份日志分析，修复 `remad` 的 SUFFIX/KEYWORD 错误，规则 0 → 34 条。

- **2026-09-29（下午）** — 确认配置文件变小（7.3M→6.4M）是订阅更新**重写文件、冲掉自有规则**所致，而非导入失败。新增 `adblock-ruleset.list`（RULE-SET 格式）作为抗覆盖方案，README 把两个坑（订阅覆盖、raw 域名被墙）提到顶部。
- **2026-09-29** — 定位到真正根因：**设备订阅更新因 `raw.githubusercontent.com` 被墙而失败**，配置始终停留在旧版本（日志验证 12 条新增规则 0 条生效）。本轮补 22 条并新增精确 `DOMAIN` 写法作 KEYWORD 兜底；README 增加"导入前必读"。规则总数 56 → 78 条。
- **2026-09-28（第三轮）** — 排查 B站开屏广告。结论：域名拦截无法实现，需 MITM 解密（用户不接受装证书），故停用相关 rewrite 规则并从 `[MITM]` 移除 `app.bilibili.com`（避免证书不受信任导致 B站请求失败）。新增 `cm.bilibili.com` 域名规则（B站商业化域，实测不承载核心 API，拦截安全但仅减少广告请求、不影响开屏）。规则总数 55 → 56 条。
- **2026-09-28（第二轮）** — 基于另一台设备日志（14:36–15:59，830 条新增）补漏。该设备规则集较旧（仅 22 条 REJECT），补入 29 条经四库核验的域名：字节系上报（`volceapplog.com` 37次、`mssdk.volces.com` 34次、`ctobsnssdk.com` 18次）、阿里系（`mum.alibabachengdun.com` 42次、`adashx.m.taobao.com` 等）、腾讯系（`bugly.qq.com` 45次）、`effirst.com` 等。规则总数 34 → 55 条。
- **2026-09-28（初版）** — 基于三份日志（13:45–14:36）分析，修复 `remad` 的 SUFFIX/KEYWORD 错误，补拦穿山甲三集群、`effirst.com` 等 17 个漏点。
