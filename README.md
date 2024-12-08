# Network File Downloader

This project implements a system for downloading large files from multiple servers simultaneously. The file is fragmented on the servers, and the client downloads the fragments in parallel, recombining them into a complete file on completion. The system also handles server failure and supports load balancing.

## Features

- **Single Server Download**: Download a file from a single server using TCP connections.
- **Multi-Server Download**: Download file fragments from multiple servers in parallel using file segmentation and recombination.
- **Server Failure Handling**: In case of a server failure, the client retries downloading the file fragment from another available server.
- **Download Resuming**: The system allows for download resumption if interrupted.

## Requirements

- Python 3.x
- Python socket library
- Threading for concurrent operations
- Basic file system setup to store downloaded chunks

## Project Structure


    /Network-File-Downloader
    ├── /src 
    │ ├── /data 
    │ │ ├── /chunks 
    │ │ ├── /received_test.cpp 
    │ │ └── /test.cpp 
    │ ├── /single_server_download 
    │ │ ├── /client.py 
    │ │ └── /server.py 
    │ ├── /multi_server_download 
    │ │ ├── /client.py 
    │ │ ├── /start_worker.py 
    │ │ └── /worker_server.py 
    ├── /.gitignore 
    ├── /LICENSE 
    ├── /README.md

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/Network-File-Downloader.git
    cd Network-File-Downloader
    ```

2. Install dependencies (if any, although this project relies on Python's built-in libraries):
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Single Server Download

1. **Start the server**:
   - Navigate to the `src/single_server_download` directory.
     ```bash
     cd src/single_server_download
     ```
   - Run the server:
     ```bash
     python server.py
     ```
   
2. **Start the client**:
   - In another terminal window, navigate to the `src/single_server_download` directory.
   - Add the file name at the end of the file.
   - Run the client:
     ```bash
     python client.py
     ```

### Multi-Server Download

1. **Start the worker servers**:
   - Navigate to the `src/multi_server_download` directory.
     ```bash
     cd src/multi_server_download
     ```
   - Run the worker servers:
     ```bash
     python start_worker.py
     ```

2. **Start the client**:
   - In another terminal window, navigate to the `src/multi_server_download` directory.
   - Add the file name at the end of the file.
   - Run the client to download the file:
     ```bash
     python client.py
     ```

### File Segmentation

In multi-server downloading, files are segmented into chunks and downloaded concurrently. The `client.py` divides the file into chunks and requests each chunk from different worker servers. Once the chunks are downloaded, the client recombines them into the original file.

### Server Failure Handling

In case of a worker server failure, the client will automatically retry downloading from the other available servers. The client uses a round-robin mechanism to balance the load and make sure that chunks are downloaded efficiently.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- This project utilizes Python's socket programming and threading modules.