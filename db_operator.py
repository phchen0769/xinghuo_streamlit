import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from file_operator import *


# 建立ORM基础类
Base = declarative_base()


# 定义Question的ORM映射
class Question(Base):
    # 指定本类映射到questions表
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 指定question映射到question字段; question字段为字符串类形
    question = Column(String(300))
    answer = Column(String(100))
    score = Column(Integer)
    creator = Column(String(16))
    class_name = Column(String(16))
    add_time = Column(String(16))


# 定义Student的ORM映射
class Student(Base):
    # 指定本类映射到questions表
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    class_name = Column(String(16))
    score = Column(Integer)


# excel导入数据库表questions
def to_sql_questions(xls_df, class_name, creator):
    # 创建数据库连接引擎
    engine = create_engine("sqlite:///myDB.db", echo=True)
    # 建立session对象
    Session = sessionmaker(bind=engine)
    session = Session()

    # 获取标准答案
    stander_answer = list(read_data("questions", "answer and score", "admin", "21软件2"))
    i = 0

    # 数据写入数据库
    for row in xls_df.values:
        # 答案处理
        try:
            answer = row[2]
            # 获取答案，去除前后空格并转换成小写
            answer = answer.lower().strip()
        except:
            answer = ""

        # 如果xls中读取的score为空，说明它是学生提交的答案
        try:
            # score列有数据，说明是标准答案
            score = row[3]

        except:
            # score列没有数据，说明是学生答案，需要核对答案。
            # res = read_data(
            #     table_name="questions",
            #     clum="score and answer",
            #     creator="admin",
            #     class_name="21软件2",
            # )
            try:
                if stander_answer[i][0] == answer:
                    score = stander_answer[i][1]
            except:
                score = "请先导入标准答案。"

        question_obj = Question(
            question=row[1],
            answer=answer,
            score=score,
            add_time=datetime.now(),
            class_name=class_name,
            creator=creator,
        )
        session.add(question_obj)

        i += 1

    # 保存
    session.commit()
    session.close()
    return True


# df导入数据库表students
# def write_student(name, score, class_name="21软件2"):
#     # 创建数据库连接引擎
#     engine = create_engine("sqlite:///myDB.db", echo=True)
#     # 建立session对象
#     Session = sessionmaker(bind=engine)
#     session = Session()

#     # 数据写入数据库
#     student_obj = Student(
#         name=name,
#         class_name=class_name,
#         score=score,
#     )
#     session.add(student_obj)

#     # 保存
#     session.commit()
#     session.close()
#     return True


# 读取数据库中的数据
# @st.cache_data
def out_sql(table_name):
    # 创建数据库连接引擎
    engine = create_engine("sqlite:///myDB.db", echo=True)
    sql_command = f"select * from {table_name}"
    return pd.read_sql(sql_command, engine)


# 读取
def read_data(table_name, clum, creator, class_name):
    engine = create_engine("sqlite:///myDB.db", echo=True)
    sql_command = f"select {clum} from {table_name} where creator = '{creator}' and class_name = '{class_name}'"
    return pd.read_sql(sql_command, engine)


# 清空question数据表中的数据
def del_data(id):
    # 创建数据库连接引擎
    engine = create_engine("sqlite:///myDB.db", echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    if id:
        session.query(Question).filter(Question.id == id).delete()
    else:
        session.query(Question).delete()
    session.commit()
    session.close()
    return True


if __name__ == "__main__":
    # 从excel导入数据到数据库
    files_name = get_files_name("answers")
    for name in files_name:
        xls_df = read_xlsx(name)
        class_name = name.split(".")[0].split("/")[1].split(" ")[0]
        try:
            creator = class_name = name.split(".")[0].split("/")[1][-3:]
        except:
            creator = ""
        finally:
            to_sql_questions(xls_df, class_name, creator)

    # 删除id=1的数据
    # del_data(1)

    # 删除所有数据
    # del_data(0)
