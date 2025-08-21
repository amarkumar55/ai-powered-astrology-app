from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
import re
from utlity.lo_shu_grid import get_number_detail, get_combination_available
from datetime import datetime

class LoshuGridPredictionAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        birth_date = request.data.get('birth_date', '').strip()  # Expecting YYYY-MM-DD

        # Validate input
        if not first_name or not last_name or not birth_date:
            return Response({'error': 'first_name, last_name, and birth_date are required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'birth_date must be in YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)

        # Initialize a dictionary for digits 1 to 9
        numbers = {i: {"count": 0, "detail": {}} for i in range(1, 10)}
        digits = [int(d) for d in re.findall(r'\d', str(birth_date_obj)) if d != '0']
        data = {
            "name": f"{first_name} {last_name}".strip(),
            "date_of_birth": birth_date_obj.isoformat(),
            "arrows_of_strength": [],
            "numbers": numbers,
            "digits": digits,
        }
        # Check for arrow combinations and add descriptions
        if 1 in digits and 5 in digits and 9 in digits:
            data['arrows_of_strength'].append(get_combination_available('1_5_9'))
        if 4 in digits and 5 in digits and 9 in digits:
            data['arrows_of_strength'].append(get_combination_available('4_5_9'))
        if 7 in digits and 5 in digits and 3 in digits:
            data['arrows_of_strength'].append(get_combination_available('7_5_3'))
        if 2 in digits and 5 in digits and 8 in digits:
            data['arrows_of_strength'].append(get_combination_available('2_5_8'))
        if 1 in digits and 4 in digits and 7 in digits:
            data['arrows_of_strength'].append(get_combination_available('1_4_7'))
        if 3 in digits and 5 in digits and 7 in digits:
            data['arrows_of_strength'].append(get_combination_available('3_5_7'))
        if 3 in digits and 6 in digits and 9 in digits:
            data['arrows_of_strength'].append(get_combination_available('3_6_9'))
        # Count the occurrences of each digit
        for digit in digits:
            numbers[digit]["count"] += 1
        # Prepare detail for each number present using the utility function
        for digit in range(1, 10):
            if digit in digits:
                numbers[digit]["detail"] = get_number_detail(str(digit))
        data['numbers'] = numbers
        return Response(data, status=status.HTTP_200_OK) 