import sys
import os
import json
import sqlite3
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QUrl, QTimer, pyqtSlot, QVariant
from PyQt5.QtGui import QGuiApplication, QIcon
from PyQt5.QtQml import QQmlApplicationEngine

class StudentManager(QObject):
    studentsUpdated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.db_file = "students.db"
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS students (
                     id TEXT PRIMARY KEY,
                     name TEXT,
                     gender TEXT,
                     age INTEGER,
                     department TEXT,
                     scores TEXT,
                     created_at TEXT,
                     updated_at TEXT)''')
        conn.commit()
        conn.close()
    
    @pyqtSlot(result="QVariantList")
    def get_all_students(self):
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("SELECT * FROM students ORDER BY created_at DESC")
            students = []
            
            for row in c.fetchall():
                student = {
                    'id': row[0],
                    'name': row[1],
                    'gender': row[2],
                    'age': row[3],
                    'department': row[4],
                    'scores': json.loads(row[5]) if row[5] else {},
                    'created_at': row[6],
                    'updated_at': row[7]
                }
                students.append(student)
            
            conn.close()
            return students
        except Exception as e:
            print(f"Error getting students: {e}")
            return []
    
    @pyqtSlot(str, result=QVariant)
    def get_student(self, student_id):
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("SELECT * FROM students WHERE id = ?", (student_id,))
            row = c.fetchone()
            
            if row:
                student = {
                    'id': row[0],
                    'name': row[1],
                    'gender': row[2],
                    'age': row[3],
                    'department': row[4],
                    'scores': json.loads(row[5]) if row[5] else {},
                    'created_at': row[6],
                    'updated_at': row[7]
                }
                conn.close()
                return student
            else:
                conn.close()
                return None
        except Exception as e:
            print(f"Error getting student: {e}")
            return None    @pyqtSlot(QVariant, result=bool)
    def add_student(self, student_data):
        try:
            # 将 QJSValue 转换为 Python 字典
            data = {}
            if 'id' in student_data:
                data['id'] = student_data['id']
            if 'name' in student_data:
                data['name'] = student_data['name']
            if 'gender' in student_data:
                data['gender'] = student_data['gender']
            if 'age' in student_data:
                data['age'] = student_data['age']
            if 'department' in student_data:
                data['department'] = student_data['department']
              # 处理成绩数据
            scores = {}
            if 'scores' in student_data:
                scores_obj = student_data['scores']
                print(f"处理成绩数据 - 原始对象: {scores_obj}, 类型: {type(scores_obj)}")
                
                # 处理不同类型的成绩数据
                if isinstance(scores_obj, dict):
                    scores = scores_obj  # 如果已经是字典直接使用
                else:
                    # 如果是 QJSValue 对象，尝试遍历其键值对
                    for subject in scores_obj.keys():
                        try:
                            scores[subject] = float(scores_obj[subject])  # 确保分数是数字
                            print(f"添加成绩: {subject} = {scores[subject]}")
                        except Exception as e:
                            print(f"处理成绩时出错: {e}")
                
            data['scores'] = scores
            print(f"最终成绩数据: {data['scores']}")
            
            print(f"添加学生: {data['name']}, 成绩数据: {data['scores']}")
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            
            now = datetime.now().isoformat()
            scores_json = json.dumps(data['scores'])
            print(f"转换后的成绩JSON: {scores_json}")
            c.execute('''INSERT INTO students 
                         (id, name, gender, age, department, scores, created_at, updated_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (data['id'], 
                      data['name'], 
                      data['gender'], 
                      data['age'], 
                      data['department'], 
                      scores_json,
                      now,                      now))
            conn.commit()
            conn.close()
            self.studentsUpdated.emit()
            print(f"学生 {data['name']} 添加成功")
            return True
        except Exception as e:
            print(f"Error adding student: {e}")
            return False
    
    @pyqtSlot(str, QVariant, result=bool)
    def update_student(self, student_id, update_data):
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            
            now = datetime.now().isoformat()
            
            # 构建更新语句
            set_clause = []
            values = []
            
            for field, value in update_data.items():
                if field == 'scores':
                    set_clause.append("scores = ?")
                    values.append(json.dumps(value))
                else:
                    set_clause.append(f"{field} = ?")
                    values.append(value)
            
            set_clause.append("updated_at = ?")
            values.append(now)
            
            query = f"UPDATE students SET {', '.join(set_clause)} WHERE id = ?"
            values.append(student_id)
            
            c.execute(query, values)
            conn.commit()
            conn.close()
            self.studentsUpdated.emit()
            return True
        except Exception as e:
            print(f"Error updating student: {e}")
            return False
    
    @pyqtSlot(str, result=bool)
    def delete_student(self, student_id):
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("DELETE FROM students WHERE id = ?", (student_id,))
            conn.commit()
            conn.close()
            self.studentsUpdated.emit()
            return True
        except Exception as e:
            print(f"Error deleting student: {e}")
            return False
    
    @pyqtSlot(float, result=str)
    def calculate_grade(self, score):
        if score >= 90: return 'A'
        elif score >= 80: return 'B'
        elif score >= 70: return 'C'
        elif score >= 60: return 'D'
        else: return 'F'
    
    @pyqtSlot(QVariant, result=float)
    def get_average_score(self, scores):
        if not scores: return 0
        total = 0
        count = 0
        for score in scores.values():
            total += score
            count += 1
        return total / count if count > 0 else 0
    
    @pyqtSlot(str, str, int, result=bool)
    def update_student_score(self, student_id, subject, score):
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            
            # 先获取当前学生信息
            c.execute("SELECT scores FROM students WHERE id = ?", (student_id,))
            row = c.fetchone()
            
            if row:
                scores = json.loads(row[0]) if row[0] else {}
                
                # 更新成绩
                scores[subject] = score
                
                # 更新数据库
                now = datetime.now().isoformat()
                c.execute(
                    "UPDATE students SET scores = ?, updated_at = ? WHERE id = ?",
                    (json.dumps(scores), now, student_id)
                )
                
                conn.commit()
                conn.close()
                self.studentsUpdated.emit()
                return True
            else:
                conn.close()
                return False
        except Exception as e:
            print(f"Error updating student score: {e}")
            return False
    
    @pyqtSlot(str, str, result=bool)
    def delete_student_score(self, student_id, subject):
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            
            # 先获取当前学生信息
            c.execute("SELECT scores FROM students WHERE id = ?", (student_id,))
            row = c.fetchone()
            
            if row:
                scores = json.loads(row[0]) if row[0] else {}
                
                # 删除成绩                if subject in scores:
                del scores[subject]
                
                # 更新数据库
                now = datetime.now().isoformat()
                c.execute(
                    "UPDATE students SET scores = ?, updated_at = ? WHERE id = ?",
                    (json.dumps(scores), now, student_id)
                )
                
                conn.commit()
                conn.close()
                self.studentsUpdated.emit()
                return True
            else:
                conn.close()
                return False
        except Exception as e:
            print(f"Error deleting student score: {e}")
            return False
            
    @pyqtSlot(result=QVariant)
    def get_statistics(self):
        try:
            print("开始统计学生成绩数据...")
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("SELECT scores FROM students")
            rows = c.fetchall()
            conn.close()
            print(f"从数据库查询到 {len(rows)} 个学生记录")
            
            # 初始化统计数据
            stats = {
                "subjects": {},  # 每个科目的统计数据
                "totalStudents": len(rows),  # 总学生数
                "totalSubjects": 0,  # 总科目数
                "averageScore": 0,  # 所有成绩的平均分
                "highestScore": 0,  # 所有成绩的最高分
                "lowestScore": 100,  # 所有成绩的最低分
                "passRate": 0,  # 所有成绩的及格率
                "totalScores": 0  # 总成绩数
            }
            
            if not rows:
                print("没有学生记录，返回空统计")
                return stats
            
            all_scores = []  # 所有成绩的列表
            pass_count = 0  # 及格成绩数量
            
            # 处理每个学生的成绩
            for row in rows:
                if not row[0]:
                    print("发现空成绩记录，跳过")
                    continue
                
                try:
                    scores = json.loads(row[0])
                    print(f"处理一个学生成绩: {scores}")
                    
                    for subject, score in scores.items():
                        try:
                            score_value = float(score)  # 确保分数是数字
                            all_scores.append(score_value)
                            
                            print(f"科目: {subject}, 分数: {score_value}")
                            
                            # 统计及格人数
                            if score_value >= 60:
                                pass_count += 1
                            
                            # 更新每个科目的统计数据
                            if subject not in stats["subjects"]:
                                stats["subjects"][subject] = {
                                    "count": 0,
                                    "total": 0,
                                    "average": 0,
                                    "highest": 0,
                                    "lowest": 100,
                                    "passCount": 0,
                                    "passRate": 0
                                }
                            
                            subject_stats = stats["subjects"][subject]
                            subject_stats["count"] += 1
                            subject_stats["total"] += score_value
                            subject_stats["highest"] = max(subject_stats["highest"], score_value)
                            subject_stats["lowest"] = min(subject_stats["lowest"], score_value)
                            
                            if score_value >= 60:
                                subject_stats["passCount"] += 1
                            
                            # 重新计算平均分和及格率
                            subject_stats["average"] = subject_stats["total"] / subject_stats["count"]
                            subject_stats["passRate"] = subject_stats["passCount"] / subject_stats["count"] * 100
                        except Exception as e:
                            print(f"处理单个分数时错误: {e}")
                except Exception as e:
                    print(f"处理学生成绩时错误: {e}")
            
            # 更新总体统计数据
            stats["totalScores"] = len(all_scores)
            stats["totalSubjects"] = len(stats["subjects"])
            
            if all_scores:
                stats["averageScore"] = sum(all_scores) / len(all_scores)
                stats["highestScore"] = max(all_scores)
                stats["lowestScore"] = min(all_scores)
                stats["passRate"] = pass_count / len(all_scores) * 100
                
            print(f"统计完成: {stats}")
            return stats
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {
                "subjects": {},
                "totalStudents": 0,
                "totalSubjects": 0,
                "averageScore": 0,
                "highestScore": 0,
                "lowestScore": 0,
                "passRate": 0,
                "totalScores": 0,
                "error": str(e)
            }


def main():
    # 创建应用
    app = QGuiApplication(sys.argv)
    app.setWindowIcon(QIcon("app_icon.png"))
    
    # 初始化QML引擎
    engine = QQmlApplicationEngine()
    
    # 创建学生管理器
    student_manager = StudentManager()
    engine.rootContext().setContextProperty("studentManager", student_manager)
    
    # 加载QML界面
    qml_file = os.path.join(os.path.dirname(__file__), "ui.qml")
    engine.load(QUrl.fromLocalFile(qml_file))
    
    if not engine.rootObjects():
        sys.exit(-1)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
