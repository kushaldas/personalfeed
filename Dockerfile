FROM fedora:23
MAINTAINER  Kushal Das

RUN dnf install -y python3-flask python3-pip redis python3-redis
RUN dnf install -y git python3-feedparser
RUN mkdir /{source,output}
RUN cd source;git clone https://github.com/kushaldas/personalfeed.git .
ADD runfeed.sh /runfeed.sh
RUN chmod +x /runfeed.sh

EXPOSE 5000
CMD ['/runfeed.sh']
