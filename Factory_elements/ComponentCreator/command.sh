info=`route`
echo $info

curl --unix-socket /var/run/docker.sock -H "Content-Type: application/x-tar" --data-binary '@Dockerfile2.tar.gz' -X POST "http://localhost/v1.41/build?t=gcr.io/clusterekaitz/pruebas-gcis:nuevo2&dockerfile=Dockerfile_2"

docker images

echo 'holaa'