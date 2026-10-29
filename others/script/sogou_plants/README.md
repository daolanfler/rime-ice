# 搜狗植物词库

2026-09-21 下载搜狗「植物」分类四页中全部 37 个 SCEL 词库：
https://pinyin.sogou.com/dict/cate/index/16

## 生成结果

- 输出：`cn_dicts/plants_sogou.dict.yaml`。
- 原始 92,024 条；按「词语 + 拼音」去重后 66,737 条，66,660 个不同词语。
- 与当前启用的五个基础字词表按词语比较，新增 62,918 个词语。
- 已追加到 `rime_ice.dict.yaml` 的 `import_tables`，保留原词库优先级。
- 保留 SCEL 中的拼音，多音记录不合并；统一初始权重 100。
- 不重新推测多音字读音；原始词库未逐条人工校对，也包含植物学术语、病虫害等关联词。
- 原始词库中没有「阿弗雷」，此次未添加来源之外的词条。
- 来源及每个原始文件的 SHA-256、记录数见 `sources.json`。
- 原始词库权利归各自作者，格式转换不改变原有授权。

## 重现转换

`convert.py` 仅依赖 Python 标准库，读取 SCEL 的拼音索引和 UTF-16LE 词条；
严格检查文件头、词条总数、记录边界和文件结束位置，解析异常时停止。
SCEL 结构核对参考：
https://github.com/studyzy/imewlconverter/blob/master/src/ImeWlConverter.Formats/SougouScel/SougouScelImporter.cs

准备一个临时目录，内含本目录的 `sources.json`，以及按其下载地址保存的
`scel/<id>.scel` 文件。从 Rime 用户目录运行：

```sh
python others/script/sogou_plants/convert.py /tmp/sogou-plants \
  cn_dicts/plants_sogou.dict.yaml others/script/sogou_plants/sources.json
```

脚本的版本和下载日期目前固定为本次导入日期；更新时应同步修改日期，
如分类有新增词库，还需更新来源清单。原始下载文件本次保存在
`/tmp/sogou-plants/scel/`，该临时路径不属于长期备份。

## 验证与生效

已使用 `rime_deployer --build` 成功编译；通过临时独立用户目录调用本机
librime，加载当前已编译的 `double_pinyin_mspy` 方案，以下词语均为首选：

| 微软双拼输入 | 候选词 |
| --- | --- |
| `boyejrmkllmu` | 薄叶卷毛梾木 |
| `yikbxtqqhlth` | 一口血秋海棠 |
| `uguihw` | 生石花 |

验证不使用、不写入个人用户词库。实际图形界面候选窗口及上屏未自动测试。
修改词库后需重新部署 Rime；只重载 Fcitx5 全局配置不能替代词库编译。

## 撤销

从 `rime_ice.dict.yaml` 删除 `- cn_dicts/plants_sogou`，重新部署即可停用。
本次修改前的入口文件备份在 `/tmp/sogou-plants/rime_ice.dict.yaml.before`。
生成词库、来源清单和转换脚本均未被 Git 忽略；本次未自动提交 Git。
