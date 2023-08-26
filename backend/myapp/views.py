from django.shortcuts import render
from numpy import sort
from .serializer import ElevatorSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Elevator, Request 
from .STATUS import Status

# Create your views here.

# *****************************************API TO INITIALIZE THE DATABASE WITH n ELEVATORS************************************************

@api_view(['GET', 'POST'])
def initialize(request):
    if request.method == 'GET':
        data = Elevator.objects.all()

        serializer = ElevatorSerializer(data, context={'request': request}, many=True)

        return Response(serializer.data)
    
    elif request.method == 'POST':
        
        total = request.data['num']
        for _ in range(total):
            Elevator.objects.create()
        return Response({'message': f'{total} elevators have been initialized.'})
    
# ***************************************API TO CHANGE THE AVAILABLITY OF AN ELEVATOR*************************************************
    
@api_view(['POST'])
def available(request):
    if request.method == 'POST':
        elev_id = request.data['id']
        elevator = Elevator.objects.filter(elevator_id = elev_id)[0]
        elevator.is_available = request.data['availability']
        elevator.save()

        return Response({'message': f'{elev_id} elevator have been set {elevator.is_available}.'})
    
# ************************************************API TO OPEN/CLOSE A DOOR**************************************************************
    
@api_view(['POST'])
def door(request):
    if request.method == 'POST':
        elev_id = request.data['id']
        status = request.data['status']
        req = Request.objects.filter(is_pending="Yes").filter(assigned_elevator_id = elev_id)
        elevator = Elevator.objects.filter(elevator_id = elev_id)[0]
        msg = "This is a default message"
        if elevator.is_available == 'No':
            msg = "Sorry the elevator is under maintainence!!"
        else:
            if status == Status.OPEN:
                if elevator.status == Status.STOP:
                    elevator.status = status
                    msg = "Door opened!!"
                elif elevator.status != Status.OPEN:
                    msg = "Elevator is in motion, door can't be opened."
            elif status == "CLOSE":
                if elevator.status == Status.OPEN:
                    elevator.status = Status.STOP
                    msg = "Door closed!!"
            else:
                msg = "Please give valid request!!"
            elevator.save()
        
        
        return Response({'status': f'Status of {elev_id} elevator have been set {elevator.status}.',
                         'message': msg})
    
# *****************************************************API TO FETCH ALL REQUESTS*********************************************************

@api_view(['POST'])
def fetchRequests(request):
    if request.method == "POST":
        elev_id = request.data['id']
        data = Request.objects.filter(assigned_elevator_id = elev_id)
        if not data:
            msg="There is no request for given elevator"
            return Response({'status': 'No data',
                         'message': msg})
        else:
            serializer = ElevatorSerializer(data, context={'request': request}, many=True)
            return Response(serializer.data)
    
# ****************************************API TO CALL AN ELEVATOR**********************************************************************

@api_view(['POST'])
def callElevator(request):
    if request.method == "POST":
        floor = request.data['floor_id']
        available_elevators = Elevator.objects.filter(is_available = "Yes").filter(status = Status.STOP)
        if not available_elevators:
            msg = "Sorry no elevators are available currently."
        else:
            elev_dict = {}
            for elevater in available_elevators:
                elev_dict[abs(elevater.cur_floor - int(floor))] = elevater
            min_dist = min(elev_dict.keys())

            # FOUND THE CLOSEST ELEVATOR
            assigned_elevator = elev_dict[min_dist]
            obj = {'dest_floor': floor, 'assigned_elevator_id': assigned_elevator.elevator_id, 'is_pending': "No"}
            req = Request(**obj)
            req.save()

            # UPDATED THE CUURENT FLOOR
            assigned_elevator.cur_floor = floor
            assigned_elevator.status = Status.OPEN
            assigned_elevator.save()
            msg = f"Assigned elevator id is {assigned_elevator.elevator_id}. Your elevator has reached floor number {floor}. The doors are open"

        return Response({'message': msg})
    
# **************************************API TO ENTER FLOORS TO GO TO****************************************************************   

@api_view(['POST'])
def enterFloor(request):
    if request.method =='POST':
        cur_floor = request.data['cur_floor']
        floors= request.data['floors'].strip().split()
        floors  = [int(f) for f in floors]

        elevator = Elevator.objects.filter(is_available = "Yes").filter(cur_floor = cur_floor).filter(status = Status.OPEN)[0]

        final_lst = find_fastest_order(floors, cur_floor)
        msg = ''
        for floor in final_lst:
            if floor < cur_floor:
                elevator.status = Status.DOWN
            else:
                elevator.status = Status.UP
            msg += f"Door closed!!  Going {elevator.status}  "
            elevator.save()

            # UPDATING THE REQUESTS TABLE
            obj = {'dest_floor': floor, 'assigned_elevator_id': elevator.elevator_id, 'is_pending': "No"}
            req = Request(**obj)
            req.save()

            msg += f"Reached floor number {floor}.  Door opened! "
            elevator.cur_floor = floor
            elevator.status = Status.OPEN
            elevator.save()
        elevator.status = Status.STOP
        elevator.save()

        return Response({'lst_of_floors': ",".join(str(f) for f in final_lst), "message": msg})

# ********************************FUNCTION TO FIND FASTEST ROUTE FOR VISITING ALL REQUESTED FLOORS************************************

def find_fastest_order(floors, cur_floor):
    floors.sort()
    down_lst = []
    up_lst = []
    for floor in floors:
        if floor < cur_floor:
            down_lst.append(floor)
        elif floor > cur_floor:
            up_lst.append(floor)
    down_lst = down_lst[::-1]
    final_list = floors
    if down_lst and up_lst:
        mx_down = abs(down_lst[-1] - cur_floor)
        mx_up = abs(up_lst[-1] - cur_floor)
        if mx_down < mx_up:
            final_list = down_lst + up_lst
        else:
            final_list = up_lst + down_lst
    else:
        final_list = down_lst + up_lst

    return final_list
    

