import mysql.connector
import json
from datetime import datetime

def export_database_to_json():
    # MySQL 연결 - 여기서 본인 비밀번호 입력!
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="0409",  # 여기에 본인 MySQL 비밀번호 입력
        database="attendance_system"
    )
    
    cursor = conn.cursor(dictionary=True)
    
    # 전체 데이터 조회
    query = """
    SELECT 
        s.student_id, s.student_number, s.name, s.major,
        w.week_id, w.week_number, w.week_name,
        COALESCE(a.attendance_status, '결석') as attendance_status,
        a.attendance_date, a.recorded_at
    FROM Students s
    CROSS JOIN Weeks w
    LEFT JOIN Attendance a ON s.student_id = a.student_id AND w.week_id = a.week_id
    ORDER BY s.student_id, w.week_number
    """
    
    cursor.execute(query)
    data = cursor.fetchall()
    
    # JSON 구조화
    output = {
        "metadata": {
            "exported_at": datetime.now().isoformat(),
            "total_students": len(set([d['student_id'] for d in data])),
            "total_weeks": len(set([d['week_id'] for d in data]))
        },
        "students": [],
        "weeks": []
    }
    
    # 학생별 데이터 구성
    students_dict = {}
    for row in data:
        student_id = row['student_id']
        if student_id not in students_dict:
            students_dict[student_id] = {
                "student_id": student_id,
                "student_number": row['student_number'],
                "name": row['name'],
                "major": row['major'],
                "attendance": {}
            }
        
        # 출석 정보 추가
        students_dict[student_id]['attendance'][row['week_number']] = {
            "status": row['attendance_status'],
            "week_name": row['week_name']
        }
    
    output['students'] = list(students_dict.values())
    
    # 주차 정보
    weeks_query = "SELECT * FROM Weeks ORDER BY week_number"
    cursor.execute(weeks_query)
    output['weeks'] = cursor.fetchall()
    
    # JSON 파일 저장
    with open('attendance.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    
    print("JSON 파일이 생성되었습니다: attendance.json")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    export_database_to_json()