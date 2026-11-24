# watchapp-app

手表应用 `.app` 安装包（由 `.hap` 打包而来），供 [watchapp](https://github.com/fanyantao4110/watchapp) 静态站下载。

站点: https://fanyantao4110.github.io/watchapp/
下载基址: https://fanyantao4110.github.io/watchapp-app/

## GT7（HUAWEI WATCH GT7）

| 应用 | 版本 | 文件 | 大小 |
|---|---|---|---|
| 2048新版 | 1.10.20260429 | 2048_gt7.app | 1.7 MB |
| ATRI -My Dear Moments- | 1.16.20260823 | atri_gt7.app | 10.4 MB |
| UNO | 1.1.1 | uno_gt7.app | 90 KB |
| a24点 | 1.0.0 | a24_gt7.app | 105 KB |
| 别踩白块 | 1.0.0 | biecaibaikuai_gt7.app | 1.2 MB |
| 扫雷 | 2.1.2 | saolei_gt7.app | 1.5 MB |
| 文件查看器 | 1.17.20260406 | fileviewer_gt7.app | 1005 KB |
| 涂鸦跳跃 | 2.1 | doodlejump_gt7.app | 1.8 MB |
| 腕上哔哩(特供版) | beta-2.0 | wristbili_gt7.app | 1.3 MB |
| 轻鸿浏览器 | 1.1.1 | qinghong_gt7.app | 1.9 MB |
| 随机事件 | 1.0.4 | randomevent_gt7.app | 6.6 MB |
| OR魂斗罗 | 1.0.7 | contra_gt7.app | 31.7 MB |
| 魔塔-正式版 | 1.0.0 | mota_gt7.app | 14.7 MB |
| MC木筏求生 | 1.0.1 | mcderaft_gt7.app | 4.6 MB |
| Wordle | 0.1.2.20250706 | wordle_gt7.app | 163 KB |
| 三国杀典藏版 | 1.0.4 | sanguosha_gt7.app | 3.1 MB |

## Fit2

| 应用 | 版本 | 文件 | 大小 |
|---|---|---|---|
| 2048 | 1.10.20260429 | 2048_fit2.app | 1.7 MB |
| kongkong | 1.0.0 | kongkong_fit2.app | 0.7 MB |
| doudizhu | 1.0.0 | doudizhu_fit2.app | 4.1 MB |
| qilei | 1.0.0 | qilei_fit2.app | 1.0 MB |
| tiaoyi | 2.4.0 | tiaoyi_fit2.app | 10.2 MB |

## 结构

每个 `.app` 是 zip，根目录一个条目（STORE 未压缩）：

```
entry-release-lite.hap     ← hap 本体，内含 config.json / resources.index / js / 图标
```

部分老包还带 `pack.info`（app 级清单，与 `pack.info.packages[0].name` 对应）。

`config.json` 里 `deviceType` 为 `liteWearable`，即鸿蒙轻量穿戴设备。

## 命名

`<英文标识>_<型号>.app`，例如：

- `2048_gt7.app` — 2048新版，GT7 版
- `doudizhu_fit2.app` — 斗地主，Fit2 版

## 许可

各应用版权归其原作者所有，此处仅作分发。若你是作者且不希望在此分发，请提 issue 或邮件联系，会尽快移除。
