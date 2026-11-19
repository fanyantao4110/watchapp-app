# watchapp-app

Fit2 手表应用的 .app 包（由原 .hap 反向转换而来）。

| 应用 | 版本 | 文件 | 大小 |
|---|---|---|---|
| 2048新版 | 1.1 | 2048_fit2.app | 1.7 MB |
| 小恐龙坤坤重置版 | 1.0.0 | kongkong_fit2.app | 0.7 MB |
| 斗地主 | 1.0.0 | doudizhu_fit2.app | 4.1 MB |
| 棋类游戏(五子,围,象棋) | 2.0 | qilei_fit2.app | 1.0 MB |
| 跳一跳,螃蟹先生 | 2.1 | tiaoyi_fit2.app | 10.2 MB |

## 结构

每个 `.app` 是一个 zip：

```
entry-release-lite.hap   (STORE，未压缩)
```

里面的 `.hap` 是 zip，含 `config.json`、`pack.info`、`resources.index`、`ets/` 等真实模块文件，可由 hap-sign-utils 重新读取（app → hap → bin），并由它签名成 `signed.bin` 形态的已签名 hap。

## 转换方式

原 `.hap` 实际是「已签名 hap」：zip 内单个 `signed.bin`，其中是 0xBE 开头的 BIN 容器（`bundleName` 长度 + 逐条目 `文件名/相对路径/内容长度/内容`，尾部带 `hw signed app   1000` 签名块）。

反向转换步骤：

1. 取出 `signed.bin`，按签名头 `subBlockSize` 找到 proBlock，截出未签名区；
2. 逐条目解析出全部真实文件（144 / 33 / 211 / 45 / 182 个）；
3. 重新打包成未签名 `.hap`（zip，STORE）；
4. 包成 `.app`（zip 内一个 STORE 的 `entry-release-lite.hap`）。

脚本：`conv.py`（与本仓库同源，可在本地复现）。

## 注意

- 原 `.hap` 的签名块在解包/重打包后不再存在，这些 `.app` 是**未签名**包；
- 要装到手表上需要走 hap-sign-utils 用你自己的 `.p12` + `.p7b` 重新签名；
- `config.json` 里的 `bundleName` 沿用原签名包的值（`drt.sign.*`），原包名保留在 `pack.info` 的 `summary.app.bundleName` 里。
