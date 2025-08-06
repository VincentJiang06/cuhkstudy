---
title: "杂项"
date: 2024-08-07
draft: false
author: "xiajiang"
tags: ["Main", "mess"]
categories: ["杂项内容"]
showSummary: false
weight: 10
description: "这是一个测试Hugo Front Matter渲染的文件"
---

# 测试Hugo Front Matter渲染

这个文件用来测试编辑器对Hugo Front Matter的特殊渲染支持。

## Front Matter 说明

上面的 YAML Front Matter 包含了Hugo的标准字段：

- **title**: 页面标题
- **date**: 创建日期
- **draft**: 是否为草稿
- **author**: 作者信息
- **tags**: 标签数组
- **categories**: 分类数组
- **showSummary**: 布尔值配置
- **weight**: 数字权重
- **description**: 页面描述

## Markdown 内容

这里是正常的Markdown内容，会按照标准方式渲染。

- 列表项目1
- 列表项目2
- 列表项目3

### 代码示例

```yaml
# 这是YAML代码块，不会被当作Front Matter处理
title: "示例"
date: 2024-08-07
```

**粗体文本** 和 *斜体文本* 正常显示。