sudo docker run -d --name video-db -e POSTGRES_USER=dbuser -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=video-db -p 4321:4321 postgres:13
cat sql-scripts/init.sql | sudo docker exec -i video-db psql -U dbuser -d video-db
