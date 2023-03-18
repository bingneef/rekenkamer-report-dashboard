VERSION=${1:-'latest'}
docker build . --platform linux/amd64 -f Dockerfile -t bingneef/rekenkamer-report-dashboard:${VERSION}
docker push bingneef/rekenkamer-report-dashboard:${VERSION}