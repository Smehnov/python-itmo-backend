## About  
App that checks lenght of uploaded document's text. (Imagine, this is gpt wrapper that summarizes text but without gpt).  
  
## Start  
```sh
docker-compose -f docker/docker-compose.yml up --build
```

##  Grafana  
```sh
http://localhost:3000/
``` 
![Grafana example](https://i.ibb.co/Y7267wW4/photo-2025-02-20-22-42-57.jpg)  
  

## Services  
- main server  
- consumer  
- postgres db  
- kafka  
- prometheus  
- grafana   
  
  
## Example of usage 
```sh
# Create Document
curl -X POST "http://localhost:8000/api/v1/documents/" \
     -H "Content-Type: application/json" \
     -d '{"title": "Sample Document", "content": "This is the document content"}'

# Get Document
curl -X GET "http://localhost:8000/api/v1/documents/1"

# List Documents
curl -X GET "http://localhost:8000/api/v1/documents/?skip=0&limit=10"

```