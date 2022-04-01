docker build -t helloapp:v1 .
docker run -v $(pwd):/docker helloapp:v1
