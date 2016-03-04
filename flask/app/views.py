from flask import render_template, jsonify, request
from motionless import AddressMarker, DecoratedMap, CenterMap, VisibleMap
from app import app
import MySQLdb

# setting up connections to cassandra
cnx = MySQLdb.connect(user="nycresto", db="nycresto", passwd="nycresto")
cursor = cnx.cursor()


@app.route('/')
@app.route('/index')
@app.route('/resto', methods=['GET'])
def resto():
    cursor.execute ("""
                SELECT distinct cuisine from restaurant ORDER BY cuisine  
                """)
    response = cursor.fetchall()
    cuisine = []
    for r in response:
        cuisine.append(r[0])
        print r
    jsonresults = [{"cuisine":c}for c in cuisine]
    return render_template("resto.html", output=jsonresults)

@app.route("/resto_post", methods=['POST'])
def resto_post():
    cuisine = request.form["cuisine"]
    boro = request.form.getlist("boro")
    grade = request.form.getlist("grade")
    in_grade = ','.join((str("\"" +g+ "\"") for g in grade))
    in_boro = ','.join((str("\"" +b+ "\"") for b in boro))
    print "Grade",  in_grade
    if len(in_grade) == 0:
        in_grade = "\"A\", \"B\", \"C\", \"D\""
    if len(in_boro) == 0:
        in_boro = "\"Manhattan\", \"Brooklyn\", \"Bronx\", \"Staten Island\", \"Queens\""

    sql = "SELECT distinct cuisine, dba, full_address  \
           FROM restaurant \
           JOIN inspection ON restaurant.camis = inspection.camis \
           WHERE cuisine = \"" + cuisine + "\" AND inspection.grade IN(" + in_grade + ") AND restaurant.boro IN(" + in_boro + ") \
           ORDER BY inspection.inspection_date DESC LIMIT 10"  
    print sql
    cursor.execute (sql)
    response = cursor.fetchall()

    dmap = DecoratedMap()
    count = 1
    mapped = 0
    results = []
    for r in response:
        match_result = {}
        match_result['dba'] = r[1]
        full_address = r[2]
        match_result['full_address'] = full_address 
        label_char = str(unichr(count+64))
        match_result['label_char'] =  label_char
        if full_address is not None:
            mapped = mapped + 1
            dmap.add_marker(AddressMarker(full_address,label=label_char))
        results.append(match_result)        
        count = count + 1
        print r

    if mapped > 0: 
        map_url =  dmap.generate_url()
    else:
        map_url = "../static/images/comedian-robot.jpg"

    if len(results) == 0:
       empty_result = {}
       empty_result['dba'] = "Sorry, no restos found "
       results.append(empty_result)

    jsonresponse = {}
    jsonresponse['map'] = map_url
    jsonresponse['restos'] = results
    print jsonresponse
    return render_template("resto_post.html", output=jsonresponse)
