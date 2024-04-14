from flask import Flask, request, jsonify, render_template
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from flask import redirect
from flask import url_for
app = Flask(__name__)

access_key = 1
secret_key = 1
region = 'ap-south-1'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/verify_credentials', methods=['POST'])
def verify_credentials():
    access_key = request.json.get('access_key')
    secret_key = request.json.get('secret_key')
    region = request.json.get('region', 'us-east-1')  # Default to us-east-1 if not specified

    if not access_key or not secret_key:
        return jsonify({'error': 'Missing AWS credentials'}), 400

    try:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        s3 = session.client('s3')
        buckets = s3.list_buckets()  # Attempt to list S3 buckets
        bucket_names = [bucket['Name'] for bucket in buckets['Buckets']]
        return jsonify({'message': 'Successfully connected to AWS', 'buckets': bucket_names}), 200
    except NoCredentialsError:
        return jsonify({'error': 'Credentials are not available'}), 403
    except PartialCredentialsError:
        return jsonify({'error': 'Incomplete credentials provided'}), 403
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidClientTokenId':
            return jsonify({'error': 'Invalid AWS credentials'}), 403
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create_bucket', methods=['POST'])
def create_bucket():
    """Create an S3 bucket in a specified region"""
    try:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=access_key,
            region_name=region
        )
        s3 = session.client('s3')
        bucket_name = request.json.get('bucket_name')
        s3.create_bucket(Bucket=bucket_name,CreateBucketConfiguration={
        'LocationConstraint': 'ap-south-1'})
        return jsonify({'message': f'Bucket {bucket_name} created successfully'}), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/launch_ec2', methods=['POST'])
def launch_ec2():
    """Launch an EC2 instance of the type specified in the request, with a given name"""
    try:
        # Create a session with AWS
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=access_key,
            region_name=region
        )
        ec2 = session.resource('ec2')
        
        # Get data from the request
        instance_type = request.json.get('instance_type')
        image_id = request.json.get('image_id')
        min_count = request.json.get('min_count', 1)  # Default is one instance
        max_count = request.json.get('max_count', 1)
        instance_name = request.json.get('instance_name')  # Instance name from the request

        # Create the instance with a name tag
        instances = ec2.create_instances(
            ImageId=image_id,
            InstanceType=instance_type,
            MinCount=min_count,
            MaxCount=max_count,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': instance_name
                        }
                    ]
                }
            ]
        )
        
        # Fetch the first instance (assuming min_count=1 for simplicity)
        instance = instances[0]
        return jsonify({'message': f'EC2 instance {instance.id} launched successfully', 'Instance ID': instance.id}), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/list_instances', methods=['GET'])
def list_instances():
    try:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        ec2 = session.resource('ec2')

        # Initialize a response list
        instances_info = []

        # Iterate through all instances
        for instance in ec2.instances.all():
            # Append instance ID and state to the list
            instances_info.append({
                'Instance ID': instance.id,
                'State': instance.state['Name']  # 'running', 'stopped', etc.
            })

        # return jsonify(instances_info), 200
        return render_template('instances.html', instances=instances_info)

    except NoCredentialsError:
        return jsonify({'error': 'Credentials are not available'}), 403
    except ClientError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/start_instance', methods=['POST'])
def start_instance():
    instance_id = request.form['instance_id']
    region = request.form.get('region', 'ap-south-1')

    try:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        ec2 = session.client('ec2')
        response = ec2.start_instances(InstanceIds=[instance_id])
        # return jsonify({'message': 'Instance started successfully', 'response': response}), 200
        return redirect(url_for('list_instances'))
    except ClientError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/stop_instance', methods=['POST'])
def stop_instance():
    """Stop an EC2 instance."""
    instance_id = request.form['instance_id']
    region = request.form.get('region', 'ap-south-1')

    try:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        ec2 = session.client('ec2')
        response = ec2.stop_instances(InstanceIds=[instance_id])
        # return jsonify({'message': 'Instance stopped successfully', 'response': response}), 200
        return redirect(url_for('list_instances'))
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/terminate_instance', methods=['POST'])
def terminate_instance():
    """Terminate an EC2 instance."""
    instance_id = request.form['instance_id']
    region = request.form.get('region', 'ap-south-1')

    try:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        ec2 = session.client('ec2')
        response = ec2.terminate_instances(InstanceIds=[instance_id])
        # return jsonify({'message': 'Instance terminated successfully', 'response': response}), 200
        return redirect(url_for('list_instances'))
    except ClientError as e:
        return jsonify({'error': str(e)}), 500    

@app.route('/create_load_balancer', methods=['POST'])
def create_load_balancer():
    """Create a new ELB load balancer"""
    try:
        session = boto3.Session(
            aws_access_key_id=request.json.get('access_key'),
            aws_secret_access_key=request.json.get('secret_key'),
            region_name=request.json.get('region')
        )
        elb = session.client('elb')
        lb_name = request.json.get('load_balancer_name')
        listeners = [{
            'Protocol': 'HTTP',
            'LoadBalancerPort': 80,
            'InstanceProtocol': 'HTTP',
            'InstancePort': 80
        }]
        subnets = request.json.get('subnets')  # Subnet IDs must be provided in request
        security_groups = request.json.get('security_groups')  # Security group IDs
        lb = elb.create_load_balancer(
            LoadBalancerName=lb_name,
            Listeners=listeners,
            Subnets=subnets,
            SecurityGroups=security_groups
        )
        return jsonify({'message': f'Load balancer {lb_name} created successfully'}), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
