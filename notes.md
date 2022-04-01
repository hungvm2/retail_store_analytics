# login mysql cli
mysql -u root -p
# list database
show database;
# DATETIME vs TIMESTAMP
DATETIME ko tự đổi về UTC time khi lưu vào DB, còn TIMESTAMP thì tự đổi về UTC time thì lưu và convert từ local time khi query
# CHAR vs VARCHAR
char fix độ dài, còn varchar ko fix độ dài 