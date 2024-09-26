# Flask Caching Proxy API

## Overview
This Flask application acts as a cli caching proxy that forwards requests to an external API while caching responses for efficient data retrieval. 

A simple proof of concept for simple url patterns. The next version should include filtering and pagination. 

This is a solution to the roadmap.sh project caching-proxy https://roadmap.sh/projects/caching-server

## Features
- Caches GET responses using Redis for improved performance.
- Forwards requests for all HTTP methods (GET, POST, PUT, DELETE).
- Handles error logging for Redis and HTTP request failures.

## Installation
1. Clone the repository: `git clone https://github.com/yourusername/repo.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables: 
4. Start the Flask application: `python3 app.py --port 3000 --origin yourapi.com --clear cache`
       Port and origin are optional. These default to 300o and http://dummyjson.com. Add '-clear cache' to flush the redis cache.  

## Usage
### Endpoint
- **GET /<url>**: Retrieve data from the external API, returning cached data if available.
- **GET /<url>/<id>**: Retrieve a single data item from the external API
- **POST /<url>**: Send data to the external API.
- **PUT /<url>/<id>**: Update data at the external API.
- **PATCH /<url/</id>**: Update data at the external API.
- **DELETE /<url>/<id>**: Remove data from the external API.

### Example Request
`curl -X GET http://localhost:5000/resource`

## Dependencies
- Flask
- Redis
- urllib3

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements.

## License
This project is licensed under the MIT License.
