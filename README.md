# AD — 广告拦截规则维护


## 文件

| 文件 | 说明 |
|---|---|
| `adblock-ruleset.list` | **推荐用法**：RULE-SET 格式（78 条），订阅更新不会冲掉 |
| `adblock-rules.conf` | 直接粘贴格式（78 条），会被订阅更新覆盖，需重新粘贴 |
| `bilibili-splash.conf` | B站开屏广告调查结论（已停用，需 MITM 才能生效，勿导入） |
| `sr_top500_whitelist_ad.conf` | 完整配置（59782 行），含上游订阅全文 |
| `LICENSE-CC-BY-SA-4.0.txt` | 上游规则集的许可协议 |

## ⚠️ 两个坑（都踩过，都会让规则"看起来没用"）

### 坑一：规则被订阅更新冲掉

**现象**：配置导入后能用，但过一段时间广告又回来了；配置文件大小变化（如 7.3M → 6.4M）。

**原因**：`update-url` 触发的订阅更新会**重写整个配置文件**，[Rule] 段的手写规则被上游内容覆盖。

**解法（推荐）**：用 RULE-SET，规则独立存放，订阅更新不会影响：

```ini
# 在 [Rule] 段任意位置加这一行即可（REJECT 策略已在该文件内声明）
RULE-SET,https://ag-jin.github.io/AD/adblock-ruleset.list,REJECT
```

已确认 Shadowrocket 支持 `RULE-SET` 指令。用 GitHub Pages 地址（国内可达），不要用 `raw.githubusercontent.com`。

### 坑二：`raw.githubusercontent.com` 在国内被墙

**现象**：手机上从 raw 域名下载/更新配置超时失败；Shadowrocket 更新订阅时**静默失败**，界面无明确报错，配置保持原样。

**解法**：一律用 GitHub Pages 地址 `https://ag-jin.github.io/AD/...`。两者走不同 CDN，前者被墙、后者通常可直连。

**验证是否生效**：看日志里 `result` 字段。若只有早期那 20 多条规则在工作、没有 `DOMAIN-KEYWORD` 或 `DOMAIN,` 精确规则，说明新规则没进去。

> 注意：本仓库的 `sr_top500_whitelist_ad.conf` 是快照，**不要**把它的地址设为 `update-url`，否则上游规则停止更新。上游地址用 `johnshall.github.io`（国内可达）。

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

实测在七猫启动窗口（14:10–14:14）内，规则可覆盖日志中全部广告请求接口。

但**无法做到零广告**，原因：

- 广告位配置由服务端下发（`api-bs.wtzw.com` 返回内容中含广告位）
- SDK 拉不到填充时，App 可能显示占位或切换联盟重试
- 广告域名持续轮换（实测半小时内穿山甲换了 `v26` → `v5-ex` → `v9` 三个素材域）

彻底的解决方案是付费版/去广告版，域名拦截只能显著减少。

## 不要拦这些



```
api-bs.wtzw.com    api-gw.wtzw.com    api-cfg.wtzw.com
drs.wtzw.com       update.wtzw.com    xiaoshuo.wtzw.com
```

## 维护记录

- **2026-09-29（下午）** — 确认配置文件变小（7.3M→6.4M）是订阅更新**重写文件、冲掉自有规则**所致，而非导入失败。新增 `adblock-ruleset.list`（RULE-SET 格式）作为抗覆盖方案，README 把两个坑（订阅覆盖、raw 域名被墙）提到顶部。
- **2026-09-29** — 定位到真正根因：**设备订阅更新因 `raw.githubusercontent.com` 被墙而失败**，配置始终停留在旧版本（日志验证 12 条新增规则 0 条生效）。本轮补 22 条并新增精确 `DOMAIN` 写法作 KEYWORD 兜底；README 增加"导入前必读"。规则总数 56 → 78 条。
- **2026-09-28（第三轮）** — 排查 B站开屏广告。结论：域名拦截无法实现，需 MITM 解密（用户不接受装证书），故停用相关 rewrite 规则并从 `[MITM]` 移除 `app.bilibili.com`（避免证书不受信任导致 B站请求失败）。新增 `cm.bilibili.com` 域名规则（B站商业化域，实测不承载核心 API，拦截安全但仅减少广告请求、不影响开屏）。规则总数 55 → 56 条。
- **2026-09-28（第二轮）** — 基于另一台设备日志（14:36–15:59，830 条新增）补漏。该设备规则集较旧（仅 22 条 REJECT），补入 29 条经四库核验的域名：字节系上报（`volceapplog.com` 37次、`mssdk.volces.com` 34次、`ctobsnssdk.com` 18次）、阿里系（`mum.alibabachengdun.com` 42次、`adashx.m.taobao.com` 等）、腾讯系（`bugly.qq.com` 45次）、`effirst.com` 等。规则总数 34 → 55 条。
- **2026-09-28（初版）** — 基于三份日志（13:45–14:36）分析，修复 `remad` 的 SUFFIX/KEYWORD 错误，补拦穿山甲三集群、`effirst.com` 等 17 个漏点。
