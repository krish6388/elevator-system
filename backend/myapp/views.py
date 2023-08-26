from django.shortcuts import render
from .serializer import ElevatorSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Elevator, Request 
from .STATUS import Status

# Create your views here.

@api_view(['GET', 'POST'])
def initialize(request):
    if request.method == 'GET':
        data = Elevator.objects.all()

        serializer = ElevatorSerializer(data, context={'request': request}, many=True)

        return Response(serializer.data)
    
    elif request.method == 'POST':
        # return Response(
        #     {
        #         "DATA": request.data['num']
        #     }
        # )
        total = request.data['num']
        for _ in range(total):
            Elevator.objects.create()
        return Response({'message': f'{total} elevators have been initialized.'})
    
@api_view(['POST'])
def available(request):
    if request.method == 'POST':
        elev_id = request.data['id']
        elevator = Elevator.objects.filter(elevator_id = elev_id)[0]
        elevator.is_available = request.data['availability']
        elevator.save()

        return Response({'message': f'{elev_id} elevator have been set {elevator.is_available}.'})
    
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
                msg = "Door closed!!"

                pass
            else:
                msg = "Please give valid request!!"
            elevator.save()
        
        
        # elif not req:
        #     elevator.status = status
        # else:
        #     elevator.status = "UP"
        
        return Response({'status': f'Status of {elev_id} elevator have been set {elevator.status}.',
                         'message': msg})
    

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
            assigned_elevator = elev_dict[min_dist]
            obj = {'dest_floor': floor, 'assigned_elevator_id': assigned_elevator.elevator_id, 'is_pending': "No"}
            req = Request(**obj)
            req.save()
            assigned_elevator.cur_floor = floor
            assigned_elevator.status = Status.OPEN
            assigned_elevator.save()
            msg = f"Assigned elevator id is {assigned_elevator.elevator_id}. Your elevator has reached floor number {floor}. The doors are open"

        return Response({'message': msg})
    

