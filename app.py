from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime
import json


app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('profiles.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with open('schema.sql') as f:
        conn.executescript(f.read())
    conn.close()

class Profile:
    def __init__(self, id, name, phone_number, gender, dob, result):
        self.id = id
        self.name = name
        self.phone_number = phone_number
        self.gender = gender
        self.dob = dob
        self.result = result

def process_number(num):
    if len(num) > 10 or not num.isdigit():
        return "Invalid input. Please enter up to a 10-digit number."

    num = num.zfill(10)

    positions = {
        '3': (0, 0), '1': (0, 1), '9': (0, 2),
        '6': (1, 0), '7': (1, 1), '5': (1, 2),
        '2': (2, 0), '8': (2, 1), '4': (2, 2)
    }

    matrix = [['' for _ in range(3)] for _ in range(3)]

    for i, digit in enumerate(num):
        if digit in positions:
            row, col = positions[digit]
            if matrix[row][col]:
                matrix[row][col] += digit
            else:
                matrix[row][col] = digit
        elif digit == '0':
            for j in range(i - 1, -1, -1):
                if num[j] != '0':
                    row, col = positions[num[j]]
                    matrix[row][col] += '+'
                    break

    total = sum(int(digit) for digit in num) - 9
    while total > 9:
        total = sum(int(digit) for digit in str(total))

    total_position = positions[str(total)] if str(total) in positions else None
    if total_position:
        row, col = total_position
        if matrix[row][col]:
            matrix[row][col] += f"({total})"
        else:
            matrix[row][col] = f"({total})"

    fixed_width = 8
    output = "`\n"

    for i, row in enumerate(matrix):
        output += " | ".join(matrix[i][j].center(fixed_width) if matrix[i][j] else ' '.center(fixed_width) for j in range(3)) + "\n"
        if i < 2:
            output += "-" * (fixed_width * 3 + 6) + "\n"
    output += f"\nTotal = {total}\n"
    return output.strip()

def process_and_print_pyramid(number):
    digits = [int(d) for d in str(number)]

    if len(digits) > 10:
        return "Input must be a 10-digit number."

    pyramid_output = "\n"
    while len(digits) > 2:
        row = ""
        for i in range(len(digits)):
            row += str(digits[i])
            if i < len(digits) - 1:
                row += "+"
        pyramid_output += row + "\n"

        next_row = []
        for i in range(len(digits) - 1):
            sum_of_digits = digits[i] + digits[i + 1]
            if sum_of_digits > 9:
                sum_of_digits -= 9
            next_row.append(sum_of_digits)

        digits = next_row

    if len(digits) == 2:
        pyramid_output += f"{digits[0]}+{digits[1]}\nTotal = {digits[0] + digits[1]}\n"

    return pyramid_output.strip()

def process_number_pairs(num):
    if len(num) > 10 or not num.isdigit():
        return "Invalid input. Please enter a 10-digit number."
    
    very_good = {13, 31, 15, 51, 17, 71, 37, 73, 38, 83, 39, 93, 57, 75, 59, 95, 69, 96, 89, 98}
    good = {12, 21, 19, 91, 23, 32, 25, 52, 29, 92, 35, 53, 36, 63, 47, 74, 49, 94, 67, 76, 78, 87, 11, 22, 33, 44, 55, 66, 77, 88, 99}
    very_bad = {14, 41, 16, 61, 26, 62, 27, 72, 28, 82, 34, 43, 46, 64, 48, 84, 58, 85, 68, 86, 96, 79, 97, 45, 54}
    bad = {18, 81, 24, 42, 56, 65}
    result = []
    i = 0

    while i < len(num) - 1:
        if num[i] == '0':
            i += 1
            continue
        j = i + 1
        while j < len(num) and num[j] == '0':
            j += 1
        if j < len(num):
            result.append(int(num[i] + num[j]))
        i = j

    categorized = {
        "Very Good": [],
        "Good": [],
        "Very Bad": [],
        "Bad": [],
    }

    for pair in result:
        if pair in good:
            categorized["Good"].append(pair)
        elif pair in very_good:
            categorized["Very Good"].append(pair)
        elif pair in bad:
            categorized["Bad"].append(pair)
        elif pair in very_bad:
            categorized["Very Bad"].append(pair)

    return result, categorized

char_to_value = {
    **dict.fromkeys("aijqy", 1),
    **dict.fromkeys("bkr", 2),
    **dict.fromkeys("cgls", 3),
    **dict.fromkeys("dmt", 4),
    **dict.fromkeys("ehnx", 5),
    **dict.fromkeys("uvw", 6),
    **dict.fromkeys("oz", 7),
    **dict.fromkeys("fp", 8),
}

def calculate_name_value(name):
    name = name.lower()
    values = [char_to_value[char] for char in name if char in char_to_value]
    total_sum = sum(values)
    final_result = total_sum
    while final_result > 9:
        final_result = sum(int(digit) for digit in str(final_result))
    return values, total_sum, final_result

def split_into_pairs(number):
    number_str = str(number)
    return [number_str[i:i+2] for i in range(0, len(number_str), 2)]

def generate_pyramid(number):
    digits = [int(d) for d in str(number)]
    pyramid = []
    while len(digits) > 1:
        row = '+'.join(map(str, digits))
        pyramid.append(row)
        next_row = [(digits[i] + digits[i + 1] - 9) if digits[i] + digits[i + 1] > 9 else digits[i] + digits[i + 1] for i in range(len(digits) - 1)]
        digits = next_row
    pyramid.append(str(digits[0]))
    return pyramid

def process_dob(date, month, year):
    if not (1 <= date <= 31 and 1 <= month <= 12 and 1900 <= year <= 9999):
        return "Invalid input. Please enter a valid date, month, and year."
    
    positions = {
        '3': (0, 0), '1': (0, 1), '9': (0, 2),
        '6': (1, 0), '7': (1, 1), '5': (1, 2),
        '2': (2, 0), '8': (2, 1), '4': (2, 2)
    }
    
    matrix = [['' for _ in range(3)] for _ in range(3)]
    
    def add_to_matrix(value):
        for digit in str(value):
            if digit != '0' and digit in positions:
                row, col = positions[digit]
                if matrix[row][col]:
                    matrix[row][col] += digit
                else:
                    matrix[row][col] = digit
    
    date_digits = [int(d) for d in str(date).zfill(2)]
    
    if len(date_digits) == 2:
        first_digit, second_digit = date_digits
        if first_digit == 0 and second_digit != 0:
            add_to_matrix(second_digit)
        elif first_digit != 0 and second_digit == 0:
            add_to_matrix(first_digit)
        elif first_digit != 0 and second_digit != 0:
            add_to_matrix(first_digit)
            add_to_matrix(second_digit)
            date_sum = first_digit + second_digit
            add_to_matrix(date_sum)
    
    add_to_matrix(month)
    
    year_last_two = str(year)[-2:]
    for digit in year_last_two:
        if digit != '0':
            add_to_matrix(int(digit))
    
    all_digits = (
        [int(d) for d in str(date) if d != '0'] +
        [int(d) for d in str(month) if d != '0'] +
        [int(d) for d in str(year) if d != '0']
    )
    total_sum = sum(all_digits)
    
    final = sum(int(d) for d in str(total_sum))
    while final >= 10:
        final = sum(int(d) for d in str(final))
    
    add_to_matrix(final)
    
    close_numbers_map = {
        1: ("1,2,3,9", "8,6"),
        2: ("1,2,5", "none"),
        3: ("1,2,3,9", "6,5"),
        4: ("4,5,6,7,8", "1,2"),
        5: ("1,4,5,6", "2"),
        6: ("5,6,8", "1,2"),
        7: ("5,6,8", "1,2,3,9"),
        8: ("5,6,8", "1,2,9"),
        9: ("1,2,3", "5")
    }
    
    close_numbers, any_number = close_numbers_map.get(final, ("none", "none"))
    
    output = "DOB Grid:\n\n"
    for i, row in enumerate(matrix):
        output += " | ".join(cell.ljust(4) if cell else '    ' for cell in row) + "\n"
        if i < 2:
            output += "-" * ( 3 + 15) + "\n"
    
    output += f"\nCompund Number = {total_sum}\nDestiny Number = {final}\n"
    output += f"Friend: {close_numbers}\nEnemy: {any_number}\n"
    
    return output.strip(), matrix, total_sum, final

def process_dob_with_birth_number(date, month, year):
    result, matrix, total_sum, final = process_dob(date, month, year)
    
    date_digits = [int(d) for d in str(date) if d != '0']
    birth_number = sum(date_digits)
    
    while birth_number >= 10:
        birth_number = sum(int(d) for d in str(birth_number))
    
    result += f"\nBirth Number: {birth_number}"
    
    return result, matrix, total_sum, final, birth_number

def calculate_ruling_year(date, transit_date, month, year_of_birth, transit_year, transit_month):
    age = transit_year - year_of_birth
    
    if transit_month > month or transit_date > date:
        age += 1
    
    r = age % 9
    r += date
    r -= 1
    
    if r > 9:
        r = sum(int(d) for d in str(r))
    
    return r

@app.route('/')
def home():
    conn = get_db_connection()
    profiles = conn.execute('SELECT * FROM profiles ORDER BY id DESC').fetchall()
    conn.close()
    
    # Format the profiles with properly formatted dates
    formatted_profiles = []
    for profile in profiles:
        date_parts = profile['dob'].split('-')
        formatted_date = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])).strftime('%d %b %Y')
        formatted_profiles.append({
            'id': profile['id'],
            'name': profile['name'],
            'dob': formatted_date
        })
    
    return render_template('home.html', profiles=formatted_profiles)

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/analyze', methods=['POST', 'GET'])
def analyze():
    if request.method == 'POST':
        name = request.form['name']
        phone_number = request.form['mobileNumber']
        gender = request.form['gender']
        
        dob = str(request.form['date'])
        year, month, date = map(int, dob.split('-'))

        matrix_output = process_number(phone_number)
        pyramid_output = process_and_print_pyramid(phone_number)
        pairs, categorized_pairs = process_number_pairs(phone_number)

        values, name_total_sum, name_final_result = calculate_name_value(name)
        name_number = ''.join(map(str, values))
        name_pairs = split_into_pairs(name_number)
        name_pyramid = generate_pyramid(name_number)

        dob_output, dob_matrix, dob_total_sum, dob_final, birth_number = process_dob_with_birth_number(date, month, year)

        pair_colors = {}
        for pair in pairs:
            if pair in categorized_pairs["Very Good"]:
                pair_colors[pair] = "pair-very-good"
            elif pair in categorized_pairs["Good"]:
                pair_colors[pair] = "pair-good"
            elif pair in categorized_pairs["Bad"]:
                pair_colors[pair] = "pair-bad"
            elif pair in categorized_pairs["Very Bad"]:
                pair_colors[pair] = "pair-very-bad"

        result = json.dumps({
            'matrix_output': matrix_output,
            'pyramid_output': pyramid_output,
            'pairs': pairs,
            'categorized_pairs': categorized_pairs,
            'pair_colors': pair_colors,
            'name_total_sum': name_total_sum,
            'name_final_result': name_final_result,
            'name_number': name_number,
            'name_pairs': name_pairs,
            'name_pyramid': name_pyramid,
            'dob_output': dob_output,
            'dob_matrix': dob_matrix,
            'dob_total_sum': dob_total_sum,
            'dob_final': dob_final,
            'birth_number': birth_number
        })

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO profiles (name, phone_number, gender, dob, result)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, phone_number, gender, f"{year}-{month:02d}-{date:02d}", result))
        profile_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return redirect(url_for('profile_detail', profile_id=profile_id))

    elif request.method == 'GET':
        profile_id = request.args.get('id')
        if profile_id:
            return redirect(url_for('profile_detail', profile_id=profile_id))
        else:
            return redirect(url_for('home'))

@app.route('/profile/<int:profile_id>')
def profile_detail(profile_id):
    conn = get_db_connection()
    profile = conn.execute('SELECT * FROM profiles WHERE id = ?', (profile_id,)).fetchone()
    conn.close()

    if profile is None:
        return "Profile not found", 404

    result = json.loads(profile['result'])
    year, month, date = map(int, profile['dob'].split('-'))
    
    return render_template('result.html',
                           name=profile['name'],
                           phone_number=profile['phone_number'],
                           gender=profile['gender'],
                           date=date,
                           month=month,
                           year=year,
                           **result)

@app.route("/calculate_ruling_year", methods=["POST"])
def calculate_ruling_year_route():
    name = request.form.get("name")
    phone_number = request.form.get("phone_number")
    gender = request.form.get("gender")
    date = int(request.form.get("date"))
    month = int(request.form.get("month"))
    year = int(request.form.get("year"))
    transit_date = int(request.form.get("transit_date"))
    transit_month = int(request.form.get("transit_month"))
    transit_year = int(request.form.get("transit_year"))

    ruling_year = calculate_ruling_year(
        date, transit_date, month, year, transit_year, transit_month
    )

    return {"ruling_year": ruling_year}

@app.route('/saved_profiles')
def saved_profiles():
    conn = get_db_connection()
    profiles = conn.execute('SELECT * FROM profiles ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('saved_profiles.html', profiles=profiles)

@app.route('/delete_profile/<int:profile_id>', methods=['POST'])
def delete_profile(profile_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM profiles WHERE id = ?', (profile_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))




import os
PORT = int(os.getenv("PORT", 5000))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
