# AWS EC2 Instance Management Dashboard

This Flask application provides a simple web interface for managing AWS EC2 instances. Users can start, stop, and terminate EC2 instances as well as list all instances with their current statuses. Additionally, the application supports creating new S3 buckets and interacting with other AWS services.

## Features

- List all EC2 instances along with their current status (running, stopped, etc.).
- Start, stop, and terminate EC2 instances.
- Create new S3 buckets in specified regions.
- Secure handling of AWS credentials.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them:

- Python 3.6 or higher
- Flask
- Boto3
- AWS account and credentials

### Installing

A step by step series of examples that tell you how to get a development environment running:

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
