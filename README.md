## Description 

PROBLEM:
Your friend wants to find the top 10 Thai resto with grade B or better.  You are given the NYC resto data set with restuarant, inspection and violation data.

APROACH:

I went to the original data source and read more detailed description on the fields of the data set.  Then I designed a schema (see below).  This schema makes it easy to joining resto information to inspection and violation data. 

Since the problem asks for the top10, I used the Inspection date to order the results so the restos inpected more recently will be ranked higher on the assumption that its grade is more current.

An ETL approach is used in doing the challenge.  Then I also add a Google Chart (Map) in the output. 

App:

##### Query Page
![alt tag](https://github.com/loryfelnunez/roboresto/blob/master/images/roboresto_query_page.png?raw=true)

#### Result for Thai Restos in ALL Boros with Grade B and higher
![alt tag](https://github.com/loryfelnunez/roboresto/blob/master/images/roboresto_query_result.png?raw=true)

#### Result for Indonesian resto in Staten Island with Grade D
![alt tag](https://github.com/loryfelnunez/roboresto/blob/master/images/roboresto_no_results.png?raw=true)

Estimated time of doing project: a day (hours scattered through Wed, Thurs, Fri (AM))

Submitted: Friday morning 3/4. 

Updates after Friday(AM) deadline:

README update -- more description and added screenshots
 
a) EXTRACT 

Data validation was done b checking the number of fields based on the defined SCHEMA.  SCHEMA is defined by the user in the user file in data/schema.  This should correspond to the columns in the input CSV file. A schema outside the program that a user cn control makes the program extensible in the case that the schema might change.  

We also check if there are headers in the data set. 

If the data fails the validation, the program then tries some transformation to make sure edge cases are not causing the data to be invalid.  An example case is when a field has commas inside a double quote. 

If the data still fails, then we log (via stdout, ideally Python's logger module should be used).

Implementation: etl/extract_load.py  --> class InputSchema
Dependent file: data/schema.txt, full data from NYC, data/small_resto.data (subset of original data set used for testing)
               

b) TRANSFORM

There some columns that needed to be tranformed. Below are the tasks done:

Cleaned cuisine data (remove non-ascii, special chars, remove additional description).  The end goal of cleaning cuisine data is to make is as general as possible so be can cluster similar cuisines together. Cuisine data is also a query parameter so we want it to be as clean as possible to avoid MySQL errors.
Example:
Italian (Family Owned) --to--> Italian
 
Transformed dates to datetime object so they can be properly sorted in th DB.

Derived full_address by concatenating the building, street, city, zipcode fields. This full address is used in generating the map.

Implementation: etc/etract_load.py - class Data
Test file: data/small_resto.data

c) LOAD
The camis is treated as a primary key for the data. So on load we do an update if the camis already exists.  For the volation table, the violation_code is the primary key so we update the other fields if the code already exists. 

Implementation: etc/etract_load.py - class Database


## Database
MySQL was used for this dataset 

Size - Data is relatively small

Queries - Queries involve JOINS which are better supported by relational databases

### Schema

Restaurant Table
CAMIS (PRIMARY KEY) | DBA | CUISINE | BUILDING | STREET | BORO | PHONE | ZIPCODE | FULL_ADDRESS 

Violation Table
VIOLATION_CODE (PRIMARY KEY) | DESCRIPTION | CRITICAL_FLAG

Inspection
CAMIS | INSPECTION_DATE | SCORE | ACTION | GRADE | GRADE_DATE | VIOLATION_CODE | INSPECTION_TYPE

Notes: Schema above was chosen to have better views on Restaurants and Inspection to support the following queries:
Get all Restaurant(Column) with Inspection(Column)  
ex. Get the top 10 Thai restaurants with Grade B
Get the top 10 Chinese restaurants in the Bronx.

## Running
AWS t1.micro instance - one server running both web app and MySQLr (not ideal)

Python 2.7

Flask (tornado)

MySQL

Google Charts (Maps)
