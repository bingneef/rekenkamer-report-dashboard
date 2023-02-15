VERSION=${1:-'latest'}
docker build . -f Dockerfile -t bingneef/rekenkamer-report-dashboard:${VERSION}
docker push bingneef/rekenkamer-report-dashboard:${VERSION}