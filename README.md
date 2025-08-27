## Running on EC2

This section describes how to deploy and run the **Semantic Search API** on an EC2 instance using Docker.

### Pre-requisites
- An **EC2 instance** with Docker installed  
- Security group configured to **allow inbound traffic on port 8000**  
- SSH access to the EC2 instance  

---

### 1. Connect to your EC2 instance
```bash
ssh -i /path/to/your-key.pem ec2-user@<EC2_PUBLIC_IP>
```

---

### 2. Clone the repository
```bash
git clone https://github.com/eternalnomad404/Semantic-SearchV6.git
cd Semantic-SearchV6
```

---

### 3. Build the Docker image
```bash
docker build -t semantic-search-api:latest .
```

---

### 4. Run the Docker container
```bash
docker run -d -p 8000:8000 semantic-search-api:latest
```

- `-d` → runs container in detached mode  
- `-p 8000:8000` → maps container port `8000` to EC2 port `8000`  

---

### 5. Access the API
Once the container is running, the API will be available at:

```
http://<EC2_PUBLIC_IP>:8000/search
```

---

### 6. Test the API using Postman
1. Open **Postman**.  
2. Set the request type to **POST**.  
3. Enter the URL:

```
http://<EC2_PUBLIC_IP>:8000/search
```

4. In the **Body** tab, select **raw** and **JSON** format.  
5. Paste the following JSON:

```json
{
  "query": "AI tools"
}
```

6. Send the request → you should receive the search results from the API.

---

### 7. Stop the container (optional)
```bash
docker ps           # list running containers
docker stop <CONTAINER_ID>
```

---

### Notes
- Ensure all **required data/models** are included in the Docker image.  
- For persistent data, consider **mounting volumes** to EC2.  
- All commands are tested for **Python 3.11-slim Docker image**.  
