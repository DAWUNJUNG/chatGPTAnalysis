from openai import OpenAI
from flask import Flask, render_template, request, Response
import json
import subprocess
from dotenv import load_dotenv
import os
import pymysql
import pandas as pd

load_dotenv(verbose=True)

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/graph', methods=['GET'])
def rGraph():
    return render_template('graph.html')


@app.route('/gptRequest', methods=['POST'])
def gptRequest():
    client = OpenAI(api_key=os.getenv('OPEN_AI_KEY'))

    language = request.form.get('language')
    wish = request.form.get('content')

    content = f"{language}언어를 사용하는 {wish} 소스코드 전달해줘"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "user", "content": content}
        ]
    )

    codeSplit = response.choices[0].message.content.split('\n')

    file = open('gptSampleSource/main.py', 'w+')

    isCode = False

    for code in codeSplit:
        if isCode == False and '```python' in code:
            isCode = True
        elif isCode == True and '```' in code:
            break

        if isCode and code != '```python' and code != '```':
            file.write(code + '\n')

    file.close()

    contentId = dbInsert(language)

    return Response(
        json.dumps({"gptMessage": response.choices[0].message.content, "contentId": contentId}),
        status=200,
        mimetype="application/json"
    )


@app.route('/checkSourceCode', methods=['POST'])
def checkSourceCode():
    requireLib = ['apscheduler']
    libs = requireLib + json.loads(request.form.get('libs'))
    contentId = request.form.get('contentId')

    try:
        result = 'false'

        if len(libs) != 0:
            for lib in libs:
                if lib == '':
                    continue
                subprocess.check_output('python -m pip install ' + lib, stderr=subprocess.STDOUT, shell=True)

        output = subprocess.check_output("python gptSampleSource/run.py", stderr=subprocess.STDOUT, shell=True,
                                         timeout=10)

        if 'Traceback' not in str(output) or 'Err' not in str(output) or 'line' not in str(output):
            result = 'true'

        dbUpdate(contentId, result)

        return Response(
            json.dumps({'result': result}),
            status=200,
            mimetype="application/json"
        )
    except Exception as e:
        if 'timed out' in str(e):
            dbUpdate(contentId, 'true')
            return Response(
                json.dumps({'result': 'true'}),
                status=200,
                mimetype="application/json"
            )
        else:
            dbUpdate(contentId, 'false')
            return Response(
                json.dumps({'result': 'false'}),
                status=200,
                mimetype="application/json"
            )


@app.route('/rGraphGenerate', methods=['POST'])
def rGraphGenerate():
    startDate = request.form.get('startData')
    endDate = request.form.get('endDate')
    getDate(startDate, endDate)
    subprocess.check_output("Rscript r/graph.R", stderr=subprocess.STDOUT, shell=True)
    return Response(
        json.dumps({'result': 'true'}),
        status=200,
        mimetype="application/json"
    )


def getDate(startDate, endDate):
    db = pymysql.connect(host=os.getenv('MYSQL_HOST'), port=int(os.getenv('MYSQL_PORT')), user=os.getenv('MYSQL_ID'), password=os.getenv('MYSQL_PW'), db=os.getenv('MYSQL_DB'))
    query = f"SELECT language, count(language) as count FROM check_result WHERE createdAt BETWEEN '{startDate} 00:00:00' AND '{endDate} 23:59:59' GROUP BY language"
    df = pd.read_sql_query(query, db)
    df.to_csv('tmp/language_analysis.csv', index=False)

    query = f"SELECT result, count(result) as count FROM check_result WHERE createdAt BETWEEN '{startDate} 00:00:00' AND '{endDate} 23:59:59' GROUP BY result"
    df = pd.read_sql_query(query, db)
    df.to_csv('tmp/result_analysis.csv', index=False)


def dbInsert(language):
    db = pymysql.connect(host=os.getenv('MYSQL_HOST'), port=int(os.getenv('MYSQL_PORT')), user=os.getenv('MYSQL_ID'), password=os.getenv('MYSQL_PW'), db=os.getenv('MYSQL_DB'))

    cursor = db.cursor()
    sql = "insert into check_result (language) values (%s);"
    cursor.execute(sql, (language))
    db.commit()
    selectIdSql = "select max(id) from check_result"
    cursor.execute(selectIdSql)
    id = cursor.fetchone()[0]
    db.close()

    return id


def dbUpdate(id, result):
    db = pymysql.connect(host=os.getenv('MYSQL_HOST'), port=int(os.getenv('MYSQL_PORT')), user=os.getenv('MYSQL_ID'), password=os.getenv('MYSQL_PW'), db=os.getenv('MYSQL_DB'))

    cursor = db.cursor()
    sql = "update check_result set result = %s where id = %s"
    cursor.execute(sql, (result, id))
    db.commit()
    db.close()


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
