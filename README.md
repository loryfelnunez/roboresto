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
Get all Restaurant(Column) with Inspection(Column)  ex. Get all Thai restaurants with Grade B

## Running
AWS t1.micro instance - one server running both web app and MySQLr (not ideal)

Python 2.7

Flask (tornado)

MySQL

Google Charts (Maps)
