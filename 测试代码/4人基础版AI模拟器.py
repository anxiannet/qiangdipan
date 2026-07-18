#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《夕妖：抢地盘》V1.3 AI模拟器兼容入口。

核心实现已拆分到：测试代码/qdp_sim/

模型用途：
- human_like：正式平衡测试主模型。
- stress_attack：高频抢地盘与拖局风险压力测试，不用于正常平衡结论。
- aggressive：旧参数兼容别名，实际按stress_attack运行。

示例：
python3 测试代码/4人基础版AI模拟器.py --players 3 --ai human_like --games 3000 --json
"""

from qdp_sim.cli import main


if __name__ == "__main__":
    main()
