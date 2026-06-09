# SE Stability Analyzer

一个零依赖的 Python 命令行工具，用于分析材料或薄膜的**近场/远场屏蔽效能
(Shielding Effectiveness, SE) 稳定性**。

本项目采用直观定义：

> 同一频率下，近场 SE 与远场 SE 的绝对差值越小，屏蔽稳定性越好。

## 功能

- 读取常见 CSV 数据；
- 计算每个频点的 `|近场 SE - 远场 SE|`；
- 汇总平均差值、最大差值和均方根差值；
- 统计满足自定义差值目标的频点比例；
- 输出明细 CSV、汇总 JSON 和无需绘图库的 SVG 曲线；
- 仅使用 Python 标准库。

## 快速开始

要求 Python 3.10 或更高版本。

```powershell
git clone https://github.com/tttmark/se-stability-analyzer.git
cd se-stability-analyzer
python -m pip install -e .
se-stability examples/sample_se.csv --target-db 3
```

也可以不安装，直接从源码运行：

```powershell
$env:PYTHONPATH = "src"
python -m se_stability_analyzer examples/sample_se.csv --target-db 3
```

默认生成 `se_stability_output/`：

```text
se_stability_output/
├── frequency_detail.csv
├── se_stability.svg
└── summary.json
```

示例数据的分析结果：

```text
Frequency range: 0.5-3 GHz
Mean |near-far|: 2.336 dB
Maximum |near-far|: 3.100 dB
Within 3 dB: 10/11 (90.9%)
```

## 输入格式

CSV 必须包含以下三列，列名区分大小写：

```csv
frequency_ghz,near_se_db,far_se_db
0.50,18.2,17.1
0.75,19.4,18.0
```

- `frequency_ghz`：频率，单位 GHz，不能重复；
- `near_se_db`：近场屏蔽效能，单位 dB；
- `far_se_db`：远场屏蔽效能，单位 dB。

数据行可以不按频率排序，程序会自动排序。

## 指标定义

频点差值：

```text
delta_i = |SE_near,i - SE_far,i|
```

平均差值：

```text
mean_delta = sum(delta_i) / N
```

均方根差值：

```text
rms_delta = sqrt(sum(delta_i^2) / N)
```

这些指标均是**越小越稳定**。`--target-db` 只用于统计达标频点，不会改变原始
计算结果。项目不使用未经验证的综合评分，避免把启发式分数误认为标准指标。

## 命令行参数

```text
usage: se-stability [-h] [-o OUTPUT_DIR] [--target-db TARGET_DB]
                    [--title TITLE] input_csv
```

示例：

```powershell
se-stability my_cst_export.csv `
  --output-dir results/sample_a `
  --target-db 2.5 `
  --title "AgNW film sample A"
```

## 测试

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## 适用范围

该工具适合 CST、矢量网络分析仪或其他流程导出的、已经对齐到相同频点的近场和
远场 SE 数据。它不会自动处理：

- 不同频率网格之间的插值；
- 多次测量的不确定度传播；
- CST 工程文件解析；
- 近场/远场物理判据判定。

进行论文分析时，应在研究方法中同时说明场区判据、探针位置、参考基准和 SE
计算方式。

## 开源许可

[MIT License](LICENSE)
