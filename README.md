sudo apt install python3       
sudo apt-get update
sudo apt-get install virtualenv
virtualenv venv --python=python3




CREATE USER 'toiuser'@'localhost' IDENTIFIED BY 'toipass';
GRANT ALL PRIVILEGES ON *.* TO 'toiuser'@'localhost' WITH GRANT OPTION;


