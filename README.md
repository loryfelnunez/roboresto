# Restaurants

## Database
MySQL was used for this dataset.
Size - Data is relatively small
Queries - Queries involve JOINS which are better supported by relational databases

### Schema

Restaurant Table
CAMIS | DBA | CUISINE | ZIP | BORO | STREET | BUILDING

Violation Table
VIOLATION_CODE | DESCRIPTION | CRITICAL_FLAG

Inspection
CAMIS | TYPE | INSPECTION_DATE | SCORE | ACTION | GRADE | GRADE_DATE | VIOLATION_CODE

Notes: Schema above was chosen to have better views on Restaurants and Inspection to support the following queries:
Get all Restaurant(Column) with Inspection(Column)  ex. Get all Thai restaurants with Grade B

## Running
AWS t1.micro instance
Web server running on the same instance as MySQL server (not ideal)

Python 2.7
Flask (tornado)
MySQL
Google Chars (Maps)
