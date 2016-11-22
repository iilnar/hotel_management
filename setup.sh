#!/usr/bin/env bash
mysql_login=root
mysql_pass=password
sudo pip3 install python-telegram-bot
sudo pip3 install flask
sudo pip3 install mysqlclient
echo "Setting up mysql"
mysql -u $mysql_login --password=$mysql_pass < sql/setup.sql
echo "Filling hotels"
mysql -u $mysql_login --password=$mysql_pass hoteldb < sql/fill_hotels.sql
echo "Filling rooms category"
mysql -u $mysql_login --password=$mysql_pass hoteldb < sql/fill_room_category.sql
echo "Filling rooms"
mysql -u $mysql_login --password=$mysql_pass hoteldb < sql/fill_rooms.sql
echo "Filling staff"
mysql -u $mysql_login --password=$mysql_pass hoteldb < sql/fill_staff.sql
echo "Filling users"
mysql -u $mysql_login --password=$mysql_pass hoteldb < sql/fill_user.sql
echo "Filling bookings"
mysql -u $mysql_login --password=$mysql_pass hoteldb < sql/fill_booking.sql