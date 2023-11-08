import streamlit as st
import pandas as pd
from st_aggrid import (
    AgGrid,
    JsCode,
    DataReturnMode,
    GridUpdateMode,
    GridOptionsBuilder,
)

from db_operator import out_sql, to_sql_questions, read_xlsx, del_data, read_data

# 打开aggrid调试信息
# js_console = JsCode(
#     """
# function(e) {
#     debugger;
#     alert(e.node.data);
#     console.log(e);
#     console.log(e.node.data);
#     console.log(e.node.selected);
#     console.log('jay');
#     console.log(e.rowIndex);
#     return e.node.data
# };
# """
# )

# JS方法，用于增加一行到AgGrid表格
js_add_row = JsCode(
    """
function(e) {
    let api = e.api;
    let rowPos = e.rowIndex + 1;
    // 数据转换成JSON
    api.applyTransaction({addIndex: rowPos, add: [{}]})
    };
"""
)

# 为'🌟'列增加一个按钮
cellRenderer_addButton = JsCode(
    """
    class BtnCellRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
            <span>
                <style>
                .btn_add {
                    background-color: #EAECEE;
                    # border: 1px solid black;
                    color: #AEB6BF;
                    text-align: center;
                    display: inline-block;
                    font-size: 12px;
                    font-weight: bold;
                    height: 2em;
                    width: 5em;
                    border-radius: 12px;
                    padding: 0px;
                }
                </style>
                <button id='click-button' 
                    class="btn_add" 
                    >&#x2193; 添加</button>
            </span>
        `;
        }
        getGui() {
            return this.eGui;
        }
    };
    """
)


# 定义动态表格，并返回操作数据
def aggrid(question_df):
    if question_df.empty:
        # 创建一个空容器，用于占位
        container = st.container()
        container.markdown("# 题目为空！")
    else:
        gd = GridOptionsBuilder.from_dataframe(question_df)
        # 打开ag-grid调试信息,选择后输出调试信息
        # gd.configure_grid_options(onRowSelected=js_console)
        # 配置列的默认设置
        # gd.configure_auto_height(autoHeight=True)
        gd.configure_default_column(
            # # 可编辑
            editable=True,
        )
        gd.configure_column(
            field="id",
            header_name="序号",
            width=70,
        )
        gd.configure_column(
            field="question",
            header_name="题目",
            width=400,
        )
        gd.configure_column(
            field="answer",
            header_name="答案",
            width=120,
        )
        gd.configure_column(
            field="score",
            header_name="分数",
            width=50,
        )
        gd.configure_column(
            field="creator",
            header_name="创建者",
            width=70,
        )
        gd.configure_column(
            field="class_name",
            header_name="班级名称",
            width=70,
        )
        gd.configure_column(
            field="add_time",
            header_name="添加时间",
            width=100,
        )
        gd.configure_column(
            field="🌟",
            onCellClicked=js_add_row,
            cellRenderer=cellRenderer_addButton,
            lockPosition="left",
            width=70,
        )
        gd.configure_selection(
            selection_mode="multiple",
            use_checkbox=True,
            # 预选
            # pre_selected_rows=[{"id": 1}, {"id": 2}],
            # suppressRowClickSelection=False,
        )
        # 表格右侧工具栏
        # gd.configure_side_bar()
        # 分页
        gd.configure_pagination(
            # 取消自动分页
            paginationAutoPageSize=False,
            # 30页一分页
            paginationPageSize=30,
        )

        gridoptions = gd.build()

        # 渲染表格
        grid_res = AgGrid(
            question_df,
            gridOptions=gridoptions,
            fit_columns_on_grid_load=True,
            update_mode=GridUpdateMode.GRID_CHANGED,
            data_return_mode=DataReturnMode.AS_INPUT,
            allow_unsafe_jscode=True,
            theme="streamlit",
            # streamlit,alpine,balham,material
        )
        # 返回数据
        return grid_res


# 显示侧边栏
def show_sidebar(question_df):
    # 标题
    con_col1, con_col2 = st.sidebar.columns(2)

    with con_col1:
        # download_btn控件，下载导入模板
        with open("./template/班别_admin.xlsx", "rb") as file:
            st.download_button(
                label="下载标准答案模板",
                data=file,
                file_name="班别_admin.xlsx",
                mime="ms-excel",
            )

    with con_col2:
        # download_btn控件，下载导入模板
        with open("./template/班别_姓名.xlsx", "rb") as file:
            st.download_button(
                label="下载答题卡模板",
                data=file,
                file_name="班别_姓名.xlsx",
                mime="ms-excel",
            )

    st.sidebar.markdown("***")

    st.sidebar.warning("1、先导入标准答案答题卡，再导入学生答题卡。2、答题卡的名字一定要按照模板文档修改。")

    col1, col2 = st.sidebar.columns(2)

    show_image = False

    with col1:
        if st.sidebar.button("示例"):
            st.sidebar.image("images/1.png", "命名样例")
            st.sidebar.image("images/2.png", "表内容样例-红色内容不能修改")

    with col2:
        if st.sidebar.button("关闭"):
            show_image = not show_image

    # file_uploader控件，上传excle表
    uploaded_files = st.sidebar.file_uploader(
        label="导入数据", type=["xlsx"], accept_multiple_files=True
    )
    for uploaded_file in uploaded_files:
        if uploaded_file:
            # 根据文件名，获取班别名
            class_name = uploaded_file.name.split(".")[0].split("_")[-2]
            st.write(class_name)
            # 根据文件名，获取创建者
            # creator = uploaded_file.name.split(".")[0].split("-")[1]
            creator = uploaded_file.name.split(".")[0].split("_")[-1]
            # creator = uploaded_file.name.split(".")[0][-3:]
            # 读取上传的excel表
            df = read_xlsx(uploaded_file)
            # 数据导入数据库
            to_sql_questions(df, creator, class_name)
            st.success("导入成功！")

    st.sidebar.markdown("***")

    # 导出当前数据
    @st.cache_data
    def convert_df(question_df):
        return question_df.to_csv().encode("utf-8")

    csv = convert_df(question_df)
    st.sidebar.download_button(
        label="导出数据为excel",
        data=csv,
        file_name="答题情况.csv",
        mime="text/csv",
    )


# 显示content内容
def show_content(question_df):
    # form控件，题目不为空，显示控件
    if not question_df.empty:
        st.markdown("#### 题目")

        # form控件，表单
        with st.form("question_form"):
            # aggrid控件
            grid_res = aggrid(question_df)
            selection = grid_res["selected_rows"]

            # 设置按钮布局
            # col1, col2 = st.columns(2)

            # with col1:
            #     if st.form_submit_button("保存", help="保存修改的题目。"):
            #         if del_data(id=0) and to_sql_questions(grid_res.data):
            #             st.success("题目信息已保存！")
            #         else:
            #             st.error("保存失败！")
            # with col2:
            # form_submit_btn控件，表单提交--删除被选中题目信息
            if st.form_submit_button("删除题目", help="删除被选中题目,如果所有题目都没有被选中，则删除所有题目。"):
                if len(selection):
                    for i in selection:
                        del_data(i["id"])
                    st.success("题目已删除！")
                else:
                    if del_data(id=0):
                        st.success("题目已清空！")
                    else:
                        st.error("删除失败！")

    else:
        st.error("题目为空！请先导入数据。")


def main():
    # 隐藏made with streamlit
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    # 从数据库获取，题目信息
    question_df = out_sql("questions")

    # 显示siderbar页
    show_sidebar(question_df)

    # 显示content页
    show_content(question_df)

    st.sidebar.info("作者：陈沛华，时间：2023年11月7日")

    # congtainer内容减少padding
    st.markdown(
        """<style>
                        
                        .block-container.st-emotion-cache-z5fcl4.ea3mdgi4{
                            padding:10px;
                        }
                        
                        </style>""",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
