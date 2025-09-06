
FROM alpine:3.19
RUN apk add --no-cache coturn
COPY turnserver.conf /etc/turnserver.conf
EXPOSE 3478/udp 3478/tcp
CMD ["/usr/bin/turnserver","-c","/etc/turnserver.conf","-v"]
