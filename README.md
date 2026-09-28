# AD — 广告拦截规则维护

针对 **七猫免费小说** 等 App 的定向广告拦截规则，基于真实流量日志（Shadowrocket `.db` 记录）分析得出。

## 背景

七猫是免费小说 App，广告收入是其变现方式，因此内置了**多家广告联盟聚合竞价**：

| 联盟 | 归属 | 相关域名 |
|---|---|---|
| 穿山甲 | 字节跳动 | `pangolin-sdk-toutiao*.com`、`pglstatp-toutiao.com` |
| 优量汇 | 腾讯 | `ugdtimg.com`、`gdt.qq.com` |
| 百青藤 | 百度 | `mobads.baidu.com`、`pos.baidu.com`、`bdurl.net` |
| 快手联盟 | 快手 | `adkwai.com` |
| 讯飞 AI 营销云 | 科大讯飞 | `voiceads.cn` |
| 自营广告位 | 七猫 | `*-remad.qm989.com` |

只拦一家无效，必须全拦。

## 文件

- **`adblock-rules.conf`** — 可直接导入 Shadowrocket 的规则片段

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

七猫正常加载正文必需的，拦了会白屏：

```
api-bs.wtzw.com    api-gw.wtzw.com    api-cfg.wtzw.com
drs.wtzw.com       update.wtzw.com    xiaoshuo.wtzw.com
```

## 维护记录

- **2026-09-28** — 初版。基于三份 Shadowrocket 日志（13:45–14:36）分析，修复 `remad` 的 SUFFIX/KEYWORD 错误，补拦穿山甲三集群、`effirst.com`（程序化广告交换，主流规则库尚未收录）等 17 个漏点。
