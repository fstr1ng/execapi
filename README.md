Тестовое задание

ssh-keygen -f ~/.ssh/id_rsa_execapi
ssh-copy-id -i ~/.ssh/id_rsa_execapi user@host
docker build . -t execapi
docker network create execapi
docker volume create execapi
docker run --network execapi --name execapi-redis  --hostname execapi-redis  -d -p 6379:6379 redis
docker run --network execapi --name execapi        --hostname execapi -v ~/.ssh/id_rsa_execapi:/root/.ssh/id_rsa_execapi -v execapi:/data -d -p 5000:5000 execapi
docker run --network execapi --name execapi-celery --hostname execapi-celery -v ~/.ssh/id_rsa_execapi:/root/.ssh/id_rsa_execapi -v execapi:/data -d execapi execapi-celery
curl -X POST -H "Content-type: application/json" -d '{"name":"example-server", "address":"185.185.69.199", "user":"root"}' localhost:5000/host

