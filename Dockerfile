FROM fedora:latest
MAINTAINER  Kushal Das

RUN dnf install -y python-flask python-pip redis python-redis
RUN dnf install -y git
RUN mkdir /{source,output}
RUN cd source;git clone https://github.com/kushaldas/personalfeed.git .
ADD runfeed.sh /runfeed.sh
RUN chmod +x /runfeed.sh

EXPOSE 5000
CMD ['/runfeed.sh']
