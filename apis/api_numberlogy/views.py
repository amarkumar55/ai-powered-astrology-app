from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from utlity.name_number import get_name_number_digit, get_name_number_mean, get_name_number_compatibility
from utlity.driver_condutor import get_combination_available, get_number_detail
from utlity.name_number import calculate_numbers, calculate_destiny_number, calculate_life_path_number, calculate_personality_number, get_destiny_number_significance, get_life_path_number_significance, get_personality_number_significance
from datetime import datetime

class NameNumberAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        if not first_name or not last_name:
            return Response({'error': 'first_name and last_name are required.'}, status=status.HTTP_400_BAD_REQUEST)
        full_name = f"{first_name} {last_name}".strip()
        name_number = get_name_number_digit(full_name)
        data = {
            "name": full_name,
            "name_number": name_number,
            "name_number_description": get_name_number_mean(name_number),
            "name_number_compatibility": get_name_number_compatibility(name_number),
        }
        return Response(data, status=status.HTTP_200_OK)

class DriverConductorAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        birth_date = request.data.get('birth_date', '').strip()
        if not first_name or not last_name or not birth_date:
            return Response({'error': 'first_name, last_name, and birth_date are required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'birth_date must be in YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)
        number_info = calculate_numbers(birth_date_obj)
        data = {
            "name": f"{first_name} {last_name}".strip(),
            "driver": number_info.get('driver_number'),
            "conductor": number_info.get('conductor_number'),
            "driver_description": get_number_detail("driver", number_info.get('driver_number')),
            "conductor_description": get_number_detail("conductor", number_info.get('conductor_number')),
            "pair_description": get_combination_available(number_info.get('driver_number'), number_info.get('conductor_number')),
        }
        return Response(data, status=status.HTTP_200_OK)

class LifePathNumberAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        birth_date = request.data.get('birth_date', '').strip()
        if not first_name or not last_name or not birth_date:
            return Response({'error': 'first_name, last_name, and birth_date are required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'birth_date must be in YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)
        life_path_number = calculate_life_path_number(birth_date_obj)
        data = {
            "name": f"{first_name} {last_name}".strip(),
            "life_path_number": life_path_number,
            "life_path_number_description": get_life_path_number_significance(life_path_number),
        }
        return Response(data, status=status.HTTP_200_OK)

class DestinyNumberAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        if not first_name or not last_name:
            return Response({'error': 'first_name and last_name are required.'}, status=status.HTTP_400_BAD_REQUEST)
        destiny_number = calculate_destiny_number(f"{first_name} {last_name}")
        data = {
            "name": f"{first_name} {last_name}".strip(),
            "destiny_number": destiny_number,
            "destiny_number_description": get_destiny_number_significance(destiny_number),
        }
        return Response(data, status=status.HTTP_200_OK)

class PersonalityNumberAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        if not first_name or not last_name:
            return Response({'error': 'first_name and last_name are required.'}, status=status.HTTP_400_BAD_REQUEST)
        personality_number = calculate_personality_number(f"{first_name} {last_name}")
        data = {
            "name": f"{first_name} {last_name}".strip(),
            "personality_number": personality_number,
            "personality_number_description": get_personality_number_significance(personality_number),
        }
        return Response(data, status=status.HTTP_200_OK) 