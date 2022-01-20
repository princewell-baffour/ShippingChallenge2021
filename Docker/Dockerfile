# The line below states we will base our new image on debian buster 
FROM debian:buster
MAINTAINER  Princewell <princewell.ba@gmail.com>

# Update the image to the latest packages, install python, python-pip, pymongo, flask and enabled CGI module in lighttpd
RUN apt-get update\
        && apt-get -y upgrade\
        && apt-get -y install python lighttpd nano python-pip python-memcache\
        && pip install pymongo==3.11\
        && pip install flask\
        && pip install waitress\
        && lighty-enable-mod cgi

# Copy the configuration files to the container
COPY lighttpd.conf /etc/lighttpd/lighttpd.conf
COPY 10-cgi.conf /etc/lighttpd/conf-available/10-cgi.conf

# Copy the index file to the correct directory on the container
COPY app/index.py /var/www/html/
# Copy the start script to the container and make it executable 
ADD start.sh /
RUN chmod +x /start.sh
# Expose ports 80 and 443
EXPOSE 80
EXPOSE 443

# Run the script
CMD ["/start.sh"]