import os
import json
import boto.sqs
import boto.sqs.queue
from boto.sqs.message import Message
from boto.sqs.connection import SQSConnection
from boto.exception import SQSError
import sys
import urllib2
from flask import Flask, Response, render_template, request

app = Flask(__name__)

def get_conn():
    response = urllib2.urlopen('http://ec2-52-30-7-5.eu-west-1.compute.amazonaws.com:81/key')
    content = response.read();
    content = content.split (':');
    response.close();
    return boto.sqs.connect_to_region("eu-west-1", aws_access_key_id=content[0], aws_secret_access_key=content[1])
  

@app.route("/")
def index():
    return """
Available API endpoints:
"""
    
@app.route("/queues", methods=['GET'])
def get_queues(): 
    """
    list all queries
    
    curl -s -X GET -H 'Accept: application/json' http://localhost:8081/queues | python -mjson.tool
    """
    all = []
    conn = get_conn()
    for q in conn.get_all_queues():
        all.append (q.name)
    resp = json.dumps(all)
    return Response(response=resp, mimetype="application/json")
  
@app.route('/queues', methods=['POST'])
def post_queues():
    """
    Create a queue
    
    curl -X POST -H 'Content-Type: application/json' http://localhost:8081/queues -d '{"name": "queue-name"}'


    """
    conn = get_conn()
    body = request.get_json(force=True)
    queue_name = body['name']
 
    q = conn.create_queue (queue_name)
    text = "Queue " + q.name + " created!"
    resp = json.dumps(text)
    return Response(response=resp, mimetype="application/json")

@app.route('/queues/<qid>', methods=['DELETE'])
def delete_queues(qid):
    """
    Delete a queue
    
    curl -X DELETE -H 'Accept: application/json' http://localhost:8081/queues/<queue_name>
    """
    conn = get_conn()
    q = conn.get_queue(qid)
    conn.delete_queue (q)

    text = q.name + " deleted!"    
    resp = json.dumps(text)
    return Response(response=resp, mimetype="application/json")

@app.route('/queues/<qid>/msgs', methods=['GET'])
def get_msgs(qid):
    """
    Get messages
    
    curl -X GET -H 'Accept: application/json' http://localhost:8081/queues/<qid>/msgs
    """
    
    conn = get_conn()
    q = conn.get_queue(qid)

    if q.count() != 0:
    	rs = q.read()
    	resp = json.dumps (rs.get_body())
    	
    return Response(response=resp, mimetype="application/json")

@app.route('/queues/<qid>/msgs/count', methods=['GET'])
def get_msgs_count(qid):

    """
    Get messages count
    
    curl -X GET -H 'Accept: application/json' http://localhost:8081/queues/<qid>
    """
    
    conn = get_conn()
    q = conn.get_queue(qid)

    text = str(q.count()) + '\n'
    resp = json.dumps(text)
    return Response(response=resp, mimetype="application/json")

@app.route('/queues/<qid>/msgs', methods=['POST'])
def post_msgs(qid):
    """
    Write message
    
    curl -s -X POST -H 'Accept: Application/json' http://localhost:8081/queues/<qid>/msgs -d '{"content": "message content"}'
    """
    
    body = request.get_json(force=True)
    queue_msg = body['content']
    
    conn = get_conn()
    q = conn.get_queue(qid)
    
    m = Message()
    m.set_body(queue_msg)
    
    q.write(m)
    
    resp = json.dumps("Message Created\n")
    return Response(response=resp, mimetype="application/json")

@app.route('/queues/<qid>/msgs', methods=['DELETE'])
def delete_msgs(qid):

    """
    Delete messages
    
    curl -X DELETE -H 'Accept: application/json' http://localhost:8081/queues/<qid>/msgs
    """
    
    conn = get_conn()
    q = conn.get_queue(qid)
            
    while q.count() > 0:
        rs = q.read()
        q.delete_message(rs)
  
    return Response(response=resp, mimetype="application/json")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
