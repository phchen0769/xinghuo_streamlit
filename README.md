# xinghuo_streamlit
创建一个基于星火3.5大模型的问答站点
# 本地运行
streamlit run main.py
# 指定端口运行
streamlit run main.py --server.port 9999

# 注意：
# 程序编写完成后，需要把docker-compose-win.yml以及Dockerfile拷贝到程序根目录（与main.py同级目录）下，cmd cd到程序根目录，后执行 docker-compose -f docker-compose-win.yml up 生成并启动容器。