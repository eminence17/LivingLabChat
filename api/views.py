async_mode = None

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RoomSerializer, MessageSerializer
from .models import Room, Message
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.decorators import api_view
from django.db.models import Q


#Socket imports
import os
from django.http import HttpResponse
import socketio

# basedir = os.path.dirname(os.path.realpath(__file__))
sio = socketio.Server(cors_allowed_origins="*", async_mode=async_mode)
thread = None

@api_view(['GET'])
def index(request):
    global thread
    if thread is None:
        thread = sio.start_background_task(background_thread)
    # return HttpResponse(open(os.path.join(basedir, 'static/index.html')))
    return HttpResponse('Connected')


def background_thread():
    count = 0
    while True:
        sio.sleep(10)
        count += 1
        sio.emit('my_response', {'data': 'Server generated event'},
                 namespace='/test')
        

@sio.event
def join(sid, message):
    room = message['room']

    sio.enter_room(sid, message['room'])
    messages = Message.objects.filter(room_id=message['room']).all()

    sio.emit('my_response', {'data': f"{sid} Joined the Room",  'count': 0}, room=room, skip_sid=sid)

    if messages.count()==0:
        sio.emit('my_response', {'data': "Hey how may i help you", 'count': 0}, room=sid)
    else:
        for i in messages:
            sio.emit('my_response', {'data': str(i.message_data), 'count': 0}, room=sid)

@sio.event
def leave(sid, message):
    sio.leave_room(sid, message['room'])
    sio.emit('my_response', {'data': 'Left room: ' + message['room']},
             room=message['room'])

def close_room(sid, message):
    sio.emit('my_response',
             {'data': 'Room ' + message['room'] + ' is closing.'},
             room=message['room'])
    sio.close_room(message['room'])
    
@sio.event
def message_event(sid, message):
    type = message['type']
    room_id = message['room_id']
    message_data = message['message_data']
    side = message['side']
    author = message['author']
    message_type = message['message_type']
    
    data = {
        "type": type,
        "room_id": room_id,
        "message_data": message_data,
        "side": side,
        "author": author,
        "message_type": message_type,
    }
    serializer = MessageSerializer(data=data)
    if serializer.is_valid():
        
        # field = {
        #     "room_id": room_id,
        #     "message_data": message_data,
        #     "side": side,
        #     "author": author,
        #     "message_type": message_type,
        #     "read": True,
        # }     
        # response = json.loads(dowellconnection(*chat, "insert", field, update_field=None))
        Message.objects.create(
            type = type,
            room_id = room_id,
            message_data = message_data,
            side = side,
            author = author,
            message_type = message_type
        )
        return sio.emit('my_response', {'data': message['message_data'], 'sid':sid},  room=message['room_id'])
    else:
        return sio.emit('my_response', {'data': 'Invalid Data', 'sid':sid}, room=message['room'])

    
#   skip_sid=sid,      
@sio.event
def disconnect_request(sid):
    sio.disconnect(sid)


    
@sio.event
def connect(sid, environ, query_para):
    sio.emit('my_response', {'data': "Welcome to Dowell Chat", 'count': 0}, room=sid)


@sio.event
def disconnect(sid):
    print('Client disconnected')