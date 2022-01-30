# Тестовое задание (python dev at Selectel)

## Установка

1. Сгенерировать ssh-ключ, добавить на удаленные машины
```
ssh-keygen -f ~/.ssh/id_rsa_execapi
ssh-copy-id -i ~/.ssh/id_rsa_execapi user@host
```

2. Собрать образ.
```
docker build . -t execapi
```

3. Создать сеть и хранилище для docker. Сеть нужна для связи по хостнеймам контейнеров, хранилище - под базу sqlite. 
```
docker network create execapi
docker volume create execapi
```

4. Создать контейнер под брокер сообщений.
```
docker run --network execapi --name execapi-redis  --hostname execapi-redis  -d -p 6379:6379 redis
```

5. Создать контейнеры с приложением. API использует два контейнера, один отвечает за прием запросов, другой - выполняет фоновые задачи (celery). Создаются из одного и того же образа, отличаются только методом запуска.
В оба контейнера прокидывается хранилище с БД и приватный ssh-ключ.

``` 
docker run --network execapi --name execapi        --hostname execapi -v ~/.ssh/id_rsa_execapi:/root/.ssh/id_rsa_execapi -v execapi:/data -d -p 5000:5000 execapi

docker run --network execapi --name execapi-celery --hostname execapi-celery -v ~/.ssh/id_rsa_execapi:/root/.ssh/id_rsa_execapi -v execapi:/data -d execapi execapi-celery
```
## Запросы

После запуска контейнеров приложение будет прослушивать 5000 порт, примеры запросов:

### Создание хоста
```
curl -X POST -H "Content-type: application/json" -d '{"name":"my-server", "address":"185.185.69.199", "user":"root"}' localhost:5000/host
```
### Получение всех хостов
```
curl -X GET -H "Content-type: application/json"  localhost:5000/host
```
### Редактирование хоста
```
curl -X POST -H "Content-type: application/json" -d '{"name":"my-server", "address":"185.185.69.199", "user":"tester"}' localhost:5000/host/my-server
```
### Вызов удаленной команды
```
curl -X POST -H "Content-type: application/json" -d '{"host":"boxik","command": "uptime"}' localhost:5000/exec
```
### Получение результата и статуса выполнения команд
```
curl -X GET -H "Content-type: application/json"  localhost:5000/exec
```
