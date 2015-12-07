from flask import Flask, request
import psycopg2
import json

#ESTABLISH CONNECTION TO DB----->
try:
    conn = psycopg2.connect("dbname='njitct' user='postgres' host='107.170.110.237' password='FuckThisProject'")
except:
    print "Unable to connect to the database"

cur = conn.cursor()
#<-----

app = Flask(__name__)

def semMap(sem):
    
    if(sem[0] == 'w'):
        sem = 'Dec-01-20' + sem[-2:]
    elif(sem[0] == 'u'):
        sem = 'Jun-01-20' + sem[-2:]
    elif(sem[0] == 'f'):
        sem = 'Sep-01-20' + sem[-2:]
    elif(sem[0] == 's'):
        sem = 'Feb-01-20' + sem[-2:]
        
    return sem


#---------------------------------------------------------------------------------------------
@app.route("/subjects")
def subjectTable():

    sem = request.args.get('semester')

    sem = semMap(sem)

    try:
        cur.execute('SELECT abbr, name FROM subject WHERE semester = \'' + sem + '\' ORDER BY abbr;')
    except Exception as e:
        print(e)
	return "Query Failed"

    subjects = list()

    for row in cur.fetchall():
        subject = {'abbr': row[0], 'name': row[1]}
        subjects.append(subject)

    return str(json.dumps(subjects))

#----------------------------------------------------------------------------------------------
@app.route("/courses")
def courseTable():

    sem = request.args.get('semester')
    subAbbr = request.args.get('subject')

    sem = semMap(sem)

    try:
        cur.execute('SELECT course.name, course.number, course.description, course.cid FROM course JOIN subject ON subject.subid = course.subid WHERE semester = \'' + sem + '\' AND subject.abbr = \'' + subAbbr + '\' ORDER BY course.number;')
    except Exception as e:
        print(e)
        return "Query Failed_1"

    courses = list()

    query1 = cur.fetchall()

    for row in query1:

        cid = str(row[3])
        sections = list()

        try:
            cur.execute('SELECT section.c_number, section.s_number, section.status, section.max, section.now, section.instructor, section.book_url, section.credits, section.sid FROM section JOIN course ON course.cid = section.cid WHERE section.cid = \'' + cid + '\' ORDER BY section.c_number;')
        except Exception as e:
            print(e)
            return "Query Failed_2"

        query2 = cur.fetchall()

        for sRow in query2:

            sid = sRow[8]
            meetings = list()

            try:
                cur.execute('SELECT meeting.start_time, meeting.end_time, meeting.day, meeting.room FROM meeting JOIN section ON section.sid = meeting.sid WHERE meeting.sid = \'' + str(sid) + '\' ;')
            except Exception as e:
                print(e)
                return "Query Failed_3"

            query3 = cur.fetchall()

            for mRow in query3:

                meeting = {'start_time': mRow[0].strftime("%I:%M %p"), 'end_time': mRow[1].strftime("%I:%M %p"), 'day': mRow[2], 'room': mRow[3]}
                meetings.append(meeting)

            section = {'call_number': sRow[0], 'section_number': sRow[1], 'status': sRow[2], 'max': sRow[3], 'now': sRow[4], 'instructor': sRow[5], 'book_url': sRow[6], 'credits': int(sRow[7]), 'meeting_time': meetings}

            sections.append(section)

        course = {'name': row[0], 'number': row[1], 'description': row[2], 'sections': sections}

        courses.append(course)


    #print(json.dumps(courses))
    return str(json.dumps(courses))

#----------------------------------------------------------------------------------------------
@app.route("/sections")
def sectionsTable():

    sem = request.args.get('semester')
    cNum = request.args.get('index')
    
    sem = semMap(sem)

    sections = list()

    try:
        cur.execute('SELECT section.c_number, section.s_number, section.status, section.max, section.now, section.instructor, section.book_url, section.credits, section.sid FROM section JOIN course ON course.cid = section.cid JOIN subject ON subject.subid = course.subid WHERE subject.semester = \'' + sem + '\' AND section.c_number = \'' + cNum + '\' ORDER BY section.c_number;')
    except Exception as e:
        print(e)
        return "Query Failed_1"

    query2 = cur.fetchall()

    

    for sRow in query2:

        sid = sRow[8]
        meetings = list()
        
        try:
            cur.execute('SELECT meeting.start_time, meeting.end_time, meeting.day, meeting.room FROM meeting JOIN section ON section.sid = meeting.sid WHERE meeting.sid = \'' + str(sid) + '\' ;')
        except Exception as e:
            print(e)
            return "Query Failed_2"

        query3 = cur.fetchall()

        for mRow in query3:

            meeting = {'start_time': mRow[0].strftime("%I:%M %p"), 'end_time': mRow[1].strftime("%I:%M %p"), 'day': mRow[2], 'room': mRow[3]}

            meetings.append(meeting)

        section = {'call_number': sRow[0], 'section_number': sRow[1], 'status': sRow[2], 'max': sRow[3], 'now': sRow[4], 'instructor': sRow[5], 'book_url': sRow[6], 'credits': int(sRow[7]), 'meeting_time': meetings}

        return str(json.dumps(section))
        #sections.append(section)

    return ""
    #print(json.dumps(sections))
    #return str(json.dumps(sections))

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 80)

#CLOSE CONNECTION----->
cur.close()
conn.close()
#<-----

