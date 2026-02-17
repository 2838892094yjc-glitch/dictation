#!/bin/bash
# 启动测试窗口 - 带唯一session
cd "/Users/yangjingchi/Desktop/自动听写"
streamlit run app.py --server.port 8502 --global.dataFrameSerialization="arrow"
