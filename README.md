# SVR Search Engine
Before reading further, make sure you are familiar with the main [SVR repository](https://github.com/TLMOS/security_video_retrieval).

## Overview
Search Engine is a web application that provides a natural language interface for searching security camera footage. It also provides a web interface for source management.

### Search
Natural language queries are converted to vectors using CLIP. Then, the closest image vectors are retrieved from Redis and the corresponding frames are retrieved from the source manager.

To search for similar vectors, Search Engine uses HNSW index provided by Redis-Search. HNSW index is a type of approximate nearest neighbor search index. It is used because it is very fast and memory efficient. It is also very easy to use, because it doesn't require any training.

### Source Management
Search Engine provides a web interface for source management. Users can add, remove, and start/stop processing of their sources. They can also view the status of their sources.

## Deployment
Essential Search Engine configuration is stored in `.env` file. You can find full list of configuration variables in `common/config.py` file.

Before deploying Search Engine, you need to deploy RabbitMQ and Redis. You can find deployment instructions in their respective README files.

After that, specify RabbitMQ and Redis credentials in `.env` file. Default usernames and passwords are already set in `.env` file, so you can use them if you didn't change them during RabbitMQ and Redis deployment. But you still need to specify RabbitMQ and Redis hostnames. (And possibly ports, if you changed them during deployment.)

After that, you can deploy Search Engine using docker-compose:
```bash
docker-compose up --build -d
```