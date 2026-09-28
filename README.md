# AD — 广告拦截规则维护


## 文件

| 文件 | 说明 |
|---|---|
| `adblock-rules.conf` | 域名规则片段（55 条），粘贴到 `[Rule]` 段顶部 |
| `bilibili-splash.conf` | 哔哩哔哩开屏广告拦截，粘贴到 `[URL Rewrite]` 段 |
| `sr_top500_whitelist_ad.conf` | 完整配置（59748 行），含上游订阅全文 |
| `LICENSE-CC-BY-SA-4.0.txt` | 上游规则集的许可协议 |

### 关于 `sr_top500_whitelist_ad.conf`

完整配置的构成：

- **上游订阅规则 59577 条（99.9%）** — 来自 [Johnshall/Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever)，采用 **CC BY-SA 4.0** 许可，署名与许可文件见本仓库
- **自有规则 55 条** — 位于 `[Rule]` 段顶部（第 12 行起），就是 `adblock-rules.conf` 的内容
- **B站开屏规则 1 条** — 位于 `[URL Rewrite]` 段，就是 `bilibili-splash.conf` 的内容
- 无任何代理节点、UUID、密码或个人凭据，可安全公开

该文件带 `update-url`，Shadowrocket 更新订阅时会重写整个文件（含自有规则）。若需长期保留自有规则，更新后重新粘贴 `adblock-rules.conf` 和 `bilibili-splash.conf`。

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

- **2026-09-28（第二轮）** — 基于另一台设备日志（14:36–15:59，830 条新增）补漏。该设备规则集较旧（仅 22 条 REJECT），补入 29 条经四库核验的域名：字节系上报（`volceapplog.com` 37次、`mssdk.volces.com` 34次、`ctobsnssdk.com` 18次）、阿里系（`mum.alibabachengdun.com` 42次、`adashx.m.taobao.com` 等）、腾讯系（`bugly.qq.com` 45次）、`effirst.com` 等。规则总数 34 → 55 条。
- **2026-09-28（初版）** — 基于三份日志（13:45–14:36）分析，修复 `remad` 的 SUFFIX/KEYWORD 错误，补拦穿山甲三集群、`effirst.com` 等 17 个漏点。
